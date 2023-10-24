import functools
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
import yaml, functools, dotenv, logging, sys
import dotenv
import yaml
from fastapi import FastAPI, HTTPException
import datetime
from typing import List
from pydantic import BaseModel, Field
import utils

# load .env variables
dotenv.load_dotenv()
# enable INFO level logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = FastAPI(
    title="Lazy Voca",
    version="1.0.0",
    description="""The Lazy Voca plugin allows you to learn new word."""
)

default_password = "123456"

class LearningWord(BaseModel):
    word: str = Field(..., description="The word to be learned (required).")
    ipa: str = Field(..., description="The International Phonetic Alphabet representation of the word.")
    meaning: str = Field(..., description="The meaning of the word.")
    examples: str = Field(..., description="Example sentences or usage of the word.")
    synonyms: str = Field(..., description="Synonyms of the word.")
    antonyms: str = Field(..., description="Antonyms of the word.")
    translation: str = Field(..., description="Translation of the word into Vietnamese.")
    collocations: str = Field(..., description="Word collocations or combinations.")
    word_families: str = Field(..., description="Related word families.")
    complexity: int = Field(..., description="Word complexity information [1:5].")
    source: str = Field(..., description="Source of the word.")
    category: str = Field(..., description="Category of the word.")
    skill: str = Field(..., description="Skill of the word.")


@app.post("/learn_new_word", description=
          """
          The request body for the "POST /learn_new_word" endpoint should be an array of objects, where each object represents a word to be learned.
          The Word must include the IPA, meaning, example sentences, synonyms, antonyms, collocations, word family, and complexity (1-5).
          If any information is missing in the content, you will supplement it using your own knowledge.
          """)
def learn_new_word(learningWords: List[LearningWord], request: Request = None):
    access_key, access_user = get_access_credentials(request)
    try:
        data = learningWords
        display_count = None
        sound = None
        user_id = get_user_id(access_user)
        conn, cursor = utils.connect_to_database()
        for i in range(0, len(data)):
            new_word = data[i].word
            ipa = data[i].ipa
            meaning = data[i].meaning
            examples = data[i].examples
            synonyms = data[i].synonyms
            antonyms = data[i].antonyms
            complexity = data[i].complexity
            word_families = data[i].word_families
            collocations = data[i].collocations
            translation = data[i].translation
            category = data[i].category
            source = data[i].source
            skill = data[i].skill
            # Check for duplication
            query = "SELECT Word FROM LazyVoca WHERE Word = %s AND user_id = %s"
            cursor.execute(query, (new_word, user_id))
            result = cursor.fetchone()
            if result:
                #update
                updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                query = "UPDATE LazyVoca SET "
                values = []
                if ipa is not None and ipa != '':
                    query += "IPA = %s, "
                    values.append(ipa)
                if meaning is not None and meaning != '':
                    query += "Meaning = %s, "
                    values.append(meaning)
                if examples is not None and examples != '':
                    query += "Examples = %s, "
                    values.append(examples)
                if complexity is not None and complexity != '':
                    query += "Complexity = %s, "
                    values.append(complexity)
                if category is not None and category != '':
                    query += "Category = %s, "
                    values.append(category)
                if source is not None and source != '':
                    query += "Source = %s, "
                    values.append(source)
                if skill is not None and skill != '':
                    query += "Skill = %s, "
                    values.append(skill)
                if display_count is not None or display_count != '':
                    query += "Display_Count = %s, "
                    values.append(display_count)
                if sound is not None and sound != '':
                    query += "Sound = %s, "
                    values.append(sound)
                if synonyms is not None and synonyms != '':
                    query += "Synonyms = %s, "
                    values.append(synonyms)
                if antonyms is not None and antonyms != '':
                    query += "Antonyms = %s, "
                    values.append(antonyms)
                if word_families is not None and word_families!= '':
                    query += "Family = %s, "
                    values.append(word_families)
                if collocations is not None and collocations != '':
                    query += "Collocations = %s, "
                    values.append(collocations)
                if translation is not None and translation != '':
                    query += "Translation = %s, "
                    values.append(translation)

                # Remove the trailing comma and space from the query
                query = query.rstrip(", ")

                # Add the WHERE clause to the query
                query += " WHERE Word = %s and user_id = %s"
                values.extend([new_word, user_id])
                cursor.execute(query, values)
                conn.commit()
                continue
            
            # Set learning status as "NEW"
            learning_status = "NEW"

            # Get the current date and time
            created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Prepare the SQL query to insert the new word into the database
            query = "INSERT INTO LazyVoca (Word, IPA, Meaning, Examples, Complexity, Category, Source, Skill, user_id, Display_Count, Sound, Synonyms, Antonyms, Family, Collocations, Translation, Learning_Status, Created, Updated) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            
            values = (new_word, ipa, meaning, examples, complexity, category, source, skill, user_id, display_count, sound, synonyms, antonyms, word_families, collocations, translation, learning_status, created, updated)

            cursor.execute(query, values)
            conn.commit()

        cursor.close()
        conn.close()

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


def get_access_credentials(request):
    access_key = request.headers.get("KMS_ACCESS_KEY")
    access_user = request.headers.get("KMS_ACCESS_USER")
    return access_key, access_user

def get_user_id(username: str):
    conn, cursor = utils.connect_to_database()

    cursor.execute("SELECT id FROM User WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    if existing_user is None:
        insert_user_sql = "INSERT INTO User (username, password) VALUES (%s, %s)"
        user_data = (username, default_password)
        cursor.execute(insert_user_sql, user_data)
        conn.commit()
        return cursor.lastrowid
        
    conn.close()
    return existing_user[0]

@app.get('/openapi.yaml', include_in_schema=False)
@functools.lru_cache()
def read_openapi_yaml(request: Request) -> Response:
    openapi_json = app.openapi()
    openapi_yaml = yaml.dump(openapi_json, sort_keys=False)
    return Response(openapi_yaml, media_type='text/yaml')
