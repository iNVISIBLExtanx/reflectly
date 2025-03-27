#!/usr/bin/env python3
"""
Mental Health Conversations Dataset Processing

This script processes the Mental Health Conversations dataset using PySpark to create:
1. Response Templates Database
2. Intervention Effectiveness Database
3. Emotional Support Patterns
"""

import os
import sys
import json
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, lit, expr, udf, regexp_replace, lower
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, ArrayType, MapType
import pyspark.sql.functions as F
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer, IDF

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Mental Health Data Processing") \
    .getOrCreate()

# Define paths
BASE_DIR = "/Users/manodhyaopallage/Refection"
RAW_DATA_PATH = f"{BASE_DIR}/data/datasets/mental_health/raw/train.csv"
PROCESSED_DIR = f"{BASE_DIR}/data/datasets/mental_health/processed"
KNOWLEDGE_DIR = f"{BASE_DIR}/data/knowledge/mental_health"

# Ensure output directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

# Define emotion keywords for classification
EMOTION_KEYWORDS = {
    'joy': ['happy', 'joy', 'excitement', 'pleased', 'delighted', 'content', 'satisfied'],
    'sadness': ['sad', 'depressed', 'unhappy', 'miserable', 'grief', 'sorrow', 'blue'],
    'anger': ['angry', 'mad', 'furious', 'annoyed', 'irritated', 'frustrated', 'rage'],
    'fear': ['afraid', 'scared', 'fearful', 'anxious', 'nervous', 'worried', 'panic'],
    'surprise': ['surprised', 'amazed', 'astonished', 'shocked', 'unexpected', 'wow', 'stunned'],
    'disgust': ['disgusted', 'grossed', 'revulsion', 'dislike', 'aversion', 'repulsed'],
    'neutral': ['neutral', 'calm', 'steady', 'okay', 'fine', 'balanced']
}

# Define intervention categories
INTERVENTION_CATEGORIES = {
    'social_connection': ['talk', 'friend', 'connect', 'call', 'family', 'socialize', 'reach out'],
    'physical_activity': ['exercise', 'walk', 'run', 'physical', 'workout', 'move', 'active'],
    'mindfulness': ['meditate', 'mindful', 'breathe', 'relax', 'present', 'awareness', 'breath'],
    'creative_expression': ['write', 'create', 'draw', 'art', 'music', 'express', 'journal'],
    'cognitive_reframing': ['reframe', 'perspective', 'think', 'mindset', 'view', 'consider', 'reflect']
}

def process_mental_health():
    """Process the Mental Health Conversations dataset and generate knowledge databases"""
    print("Loading Mental Health Conversations dataset...")
    
    # Read the CSV file
    mental_health_df = spark.read.option("header", "true").csv(RAW_DATA_PATH)
    
    # Show the schema and sample data
    mental_health_df.printSchema()
    mental_health_df.show(5, truncate=False)
    
    # Clean and preprocess the data
    clean_df = preprocess_data(mental_health_df)
    
    # Save processed data
    print("Saving processed Mental Health dataset...")
    clean_df.write.mode("overwrite").parquet(f"{PROCESSED_DIR}/conversations")
    
    # Extract emotion-specific response templates
    extract_response_templates(clean_df)
    
    # Analyze intervention effectiveness
    analyze_interventions(clean_df)
    
    # Generate emotional support patterns
    generate_support_patterns(clean_df)
    
    print("Mental Health Conversations processing complete!")

def preprocess_data(df):
    """Clean and preprocess the conversations data"""
    print("Preprocessing Mental Health Conversations data...")
    
    # Define preprocessing UDFs
    @udf(StringType())
    def clean_text(text):
        if text is None:
            return ""
        # Remove line breaks, extra spaces
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    # Apply text cleaning
    clean_df = df.withColumn("CleanContext", clean_text(col("Context")))
    clean_df = clean_df.withColumn("CleanResponse", clean_text(col("Response")))
    
    # Determine dominant emotion in context
    for emotion, keywords in EMOTION_KEYWORDS.items():
        # Create a column for each emotion using keyword matching
        keyword_pattern = '|'.join(keywords)
        clean_df = clean_df.withColumn(
            f"{emotion}_keywords", 
            F.size(F.array_remove(
                F.split(
                    F.lower(
                        F.regexp_replace(col("CleanContext"), "[^a-zA-Z0-9\\s]", " ")
                    ), 
                    "\\s+"
                ),
                ""
            )) - F.size(F.array_remove(
                F.split(
                    F.lower(
                        F.regexp_replace(
                            F.regexp_replace(col("CleanContext"), keyword_pattern, ""),
                            "[^a-zA-Z0-9\\s]", 
                            " "
                        )
                    ), 
                    "\\s+"
                ),
                ""
            ))
        )
    
    # Determine dominant emotion
    emotion_columns = [f"{emotion}_keywords" for emotion in EMOTION_KEYWORDS.keys()]
    
    for i, emotion in enumerate(EMOTION_KEYWORDS.keys()):
        if i == 0:
            dominant_emotion = when(
                col(f"{emotion}_keywords") > F.greatest(*[col(c) for c in emotion_columns if c != f"{emotion}_keywords"]),
                lit(emotion)
            )
        else:
            dominant_emotion = dominant_emotion.when(
                col(f"{emotion}_keywords") > F.greatest(*[col(c) for c in emotion_columns if c != f"{emotion}_keywords"]),
                lit(emotion)
            )
    
    # Set neutral as default if no clear dominant emotion
    dominant_emotion = dominant_emotion.otherwise(lit("neutral"))
    clean_df = clean_df.withColumn("dominant_emotion", dominant_emotion)
    
    # Identify interventions in responses
    for intervention, keywords in INTERVENTION_CATEGORIES.items():
        # Create a column for each intervention type using keyword matching
        keyword_pattern = '|'.join(keywords)
        clean_df = clean_df.withColumn(
            f"{intervention}_score", 
            F.size(F.array_remove(
                F.split(
                    F.lower(
                        F.regexp_replace(col("CleanResponse"), "[^a-zA-Z0-9\\s]", " ")
                    ), 
                    "\\s+"
                ),
                ""
            )) - F.size(F.array_remove(
                F.split(
                    F.lower(
                        F.regexp_replace(
                            F.regexp_replace(col("CleanResponse"), keyword_pattern, ""),
                            "[^a-zA-Z0-9\\s]", 
                            " "
                        )
                    ), 
                    "\\s+"
                ),
                ""
            ))
        )
    
    # Determine primary intervention
    intervention_columns = [f"{intervention}_score" for intervention in INTERVENTION_CATEGORIES.keys()]
    
    for i, intervention in enumerate(INTERVENTION_CATEGORIES.keys()):
        if i == 0:
            primary_intervention = when(
                col(f"{intervention}_score") > F.greatest(*[col(c) for c in intervention_columns if c != f"{intervention}_score"]),
                lit(intervention)
            )
        else:
            primary_intervention = primary_intervention.when(
                col(f"{intervention}_score") > F.greatest(*[col(c) for c in intervention_columns if c != f"{intervention}_score"]),
                lit(intervention)
            )
    
    # Set cognitive_reframing as default if no clear primary intervention
    primary_intervention = primary_intervention.otherwise(lit("cognitive_reframing"))
    clean_df = clean_df.withColumn("primary_intervention", primary_intervention)
    
    # Calculate response length as a proxy for complexity
    clean_df = clean_df.withColumn(
        "response_length", 
        F.length(col("CleanResponse"))
    )
    
    return clean_df

def extract_response_templates(df):
    """Extract emotion-specific response templates"""
    print("Extracting response templates...")
    
    # Group responses by dominant emotion
    emotion_responses = df.groupBy("dominant_emotion") \
        .agg(
            F.collect_list("CleanResponse").alias("responses"),
            F.count("*").alias("count")
        )
    
    # Show emotion distribution
    emotion_responses.select("dominant_emotion", "count").show()
    
    # Define a UDF to select the top responses
    @udf(ArrayType(StringType()))
    def select_top_responses(responses, count):
        # Sort responses by length (as a proxy for quality and completeness)
        sorted_responses = sorted(responses, key=len, reverse=True)
        # Select top responses (up to 10 or 20% of total, whichever is smaller)
        num_to_select = min(10, max(3, int(count * 0.2)))
        return sorted_responses[:num_to_select]
    
    # Apply the UDF to select top responses
    templates_df = emotion_responses.withColumn(
        "templates", 
        select_top_responses(col("responses"), col("count"))
    )
    
    # Convert to a more usable format
    response_templates = {}
    
    for row in templates_df.collect():
        emotion = row["dominant_emotion"]
        templates = row["templates"]
        response_templates[emotion] = templates
    
    # Save response templates
    with open(f"{KNOWLEDGE_DIR}/response_templates.json", "w") as f:
        json.dump(response_templates, f, indent=2)
    
    print("Response templates extracted!")

def analyze_interventions(df):
    """Analyze intervention effectiveness for different emotions"""
    print("Analyzing intervention effectiveness...")
    
    # Group by emotion and intervention
    effectiveness_df = df.groupBy("dominant_emotion", "primary_intervention") \
        .agg(
            F.count("*").alias("frequency"),
            F.avg("response_length").alias("avg_response_length")
        )
    
    # Calculate total frequency by emotion
    emotion_totals = effectiveness_df.groupBy("dominant_emotion") \
        .agg(F.sum("frequency").alias("total"))
    
    # Join to calculate relative frequency
    effectiveness_df = effectiveness_df.join(
        emotion_totals,
        on="dominant_emotion"
    ).withColumn(
        "relative_frequency", 
        col("frequency") / col("total")
    )
    
    # Calculate effectiveness score (using relative frequency and response length as proxies)
    effectiveness_df = effectiveness_df.withColumn(
        "effectiveness_score",
        (col("relative_frequency") * 0.7) + 
        (col("avg_response_length") / 1000.0 * 0.3)  # Normalize by typical length
    )
    
    # Normalize effectiveness score to 0-1 scale
    max_score = effectiveness_df.agg(F.max("effectiveness_score")).collect()[0][0]
    effectiveness_df = effectiveness_df.withColumn(
        "normalized_effectiveness",
        F.when(max_score > 0, col("effectiveness_score") / max_score).otherwise(0.5)
    )
    
    # Show effectiveness scores
    effectiveness_df.select(
        "dominant_emotion", 
        "primary_intervention", 
        "normalized_effectiveness"
    ).orderBy(
        "dominant_emotion", 
        col("normalized_effectiveness").desc()
    ).show()
    
    # Convert to a more usable format
    intervention_effectiveness = {}
    
    for row in effectiveness_df.collect():
        emotion = row["dominant_emotion"]
        intervention = row["primary_intervention"]
        effectiveness = float(row["normalized_effectiveness"])
        
        if emotion not in intervention_effectiveness:
            intervention_effectiveness[emotion] = []
        
        intervention_effectiveness[emotion].append({
            "intervention": intervention.replace("_", " ").title(),
            "effectiveness": effectiveness
        })
    
    # Sort interventions by effectiveness
    for emotion in intervention_effectiveness:
        intervention_effectiveness[emotion] = sorted(
            intervention_effectiveness[emotion],
            key=lambda x: x["effectiveness"],
            reverse=True
        )
    
    # Save intervention effectiveness
    with open(f"{KNOWLEDGE_DIR}/intervention_effectiveness.json", "w") as f:
        json.dump(intervention_effectiveness, f, indent=2)
    
    print("Intervention effectiveness analyzed!")

def generate_support_patterns(df):
    """Generate patterns of emotional support strategies"""
    print("Generating emotional support patterns...")
    
    # Tokenize responses
    tokenizer = Tokenizer(inputCol="CleanResponse", outputCol="words")
    tokenized_df = tokenizer.transform(df)
    
    # Remove stop words
    remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
    filtered_df = remover.transform(tokenized_df)
    
    # Extract features using CountVectorizer
    cv = CountVectorizer(inputCol="filtered_words", outputCol="word_counts", minDF=5.0)
    cv_model = cv.fit(filtered_df)
    cv_df = cv_model.transform(filtered_df)
    
    # Apply IDF to get important words
    idf = IDF(inputCol="word_counts", outputCol="features")
    idf_model = idf.fit(cv_df)
    tfidf_df = idf_model.transform(cv_df)
    
    # Get vocabulary from CountVectorizer
    vocabulary = cv_model.vocabulary
    
    # Group by emotion
    emotion_groups = tfidf_df.groupBy("dominant_emotion")
    
    # Extract support patterns
    support_patterns = {}
    
    # For each emotion, identify common response patterns
    for emotion in EMOTION_KEYWORDS.keys():
        emotion_df = tfidf_df.filter(col("dominant_emotion") == emotion)
        
        if emotion_df.count() > 0:
            # Aggregate TF-IDF vectors
            emotion_vec = emotion_df.select(F.sum("features").alias("sum_features")).first()["sum_features"]
            
            # Get top feature indices
            top_indices = sorted(range(len(emotion_vec)), key=lambda i: emotion_vec[i], reverse=True)[:20]
            
            # Get top words
            top_words = [vocabulary[i] for i in top_indices if i < len(vocabulary)]
            
            # Store patterns
            support_patterns[emotion] = {
                "keywords": top_words,
                "strategies": generate_strategies_for_emotion(emotion),
                "example_templates": get_example_templates(emotion_df, 3)
            }
    
    # Save support patterns
    with open(f"{KNOWLEDGE_DIR}/support_patterns.json", "w") as f:
        json.dump(support_patterns, f, indent=2)
    
    print("Emotional support patterns generated!")

def generate_strategies_for_emotion(emotion):
    """Generate support strategies for a specific emotion"""
    # Define default strategies for each emotion
    default_strategies = {
        'joy': [
            "Celebrate and affirm positive emotions",
            "Encourage savoring the experience",
            "Help identify what led to the positive state"
        ],
        'sadness': [
            "Validate feelings without judgment",
            "Provide gentle encouragement and hope",
            "Suggest small steps toward feeling better"
        ],
        'anger': [
            "Acknowledge frustration without escalating",
            "Offer perspective and reframing",
            "Suggest constructive channels for emotions"
        ],
        'fear': [
            "Normalize anxiety and worry",
            "Provide grounding techniques",
            "Break down concerns into manageable parts"
        ],
        'surprise': [
            "Help process unexpected information",
            "Provide space to adapt to changes",
            "Find meaning in unexpected situations"
        ],
        'disgust': [
            "Acknowledge strong negative reactions",
            "Offer distance from triggering situations",
            "Suggest reframing or boundary-setting"
        ],
        'neutral': [
            "Explore potential underlying feelings",
            "Offer general wellbeing support",
            "Suggest preventative mental health practices"
        ]
    }
    
    return default_strategies.get(emotion, [
        "Validate current feelings",
        "Offer supportive perspective",
        "Suggest adaptive coping strategies"
    ])

def get_example_templates(df, num_examples):
    """Get example response templates from the dataframe"""
    # Sort by response length (as a proxy for quality)
    sorted_df = df.orderBy(col("response_length").desc())
    
    # Get top examples
    examples = [row["CleanResponse"] for row in sorted_df.limit(num_examples).collect()]
    
    return examples

if __name__ == "__main__":
    process_mental_health()
    spark.stop()
