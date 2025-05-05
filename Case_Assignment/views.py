from django.shortcuts import render

# Create your views here.
import pandas as pd
from django.http import JsonResponse
from sentence_transformers import SentenceTransformer, util
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import os

# Load a pre-trained sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

@csrf_exempt
def process_ticket(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        
        error_message = request.POST.get('error_message')

        # Combine the input fields into one text
        input_text = f"{subject} {description} {error_message}"
        input_embedding = model.encode(input_text)

        # Load the Excel file
        excel_file_path = 'Case_Assignment/data/output_similarity_scores1.xlsx'
        df = pd.read_excel(excel_file_path)
        
        # Create embeddings for the columns in the Excel file
        df['combined_text'] = df['Subject'] + " " + df['Description'] + " " + df['Error Message']
        df['combined_text'] = df['combined_text'].fillna('')
        df['embedding'] = df['combined_text'].apply(lambda x: model.encode(x))

        # Calculate similarity score
        df['similarity_score'] = df['embedding'].apply(lambda x: util.pytorch_cos_sim(input_embedding, x).item())
        
        output_file_path = 'Case_Assignment/data/output_similarity_scores1.xlsx'
        df.to_excel(output_file_path, index=False)
        #Sort the DataFrame by similarity score in descending order
        df = df.sort_values(by='similarity_score', ascending=False)
        
        # Save the updated DataFrame to a new Excel file
        output_file_path = 'Case_Assignment/data/output_similarity_scores.xlsx'
        df.to_excel(output_file_path, index=False)
        
        # Select only the top 1000 rows based on similarity scores
        top_1000_df = df.head(20)
        
        # Calculate the sum of similarity scores by case owner for the top 1000 rows
        similarity_sum_by_owner = top_1000_df.groupby('Case Owner')['similarity_score'].sum()
        sorted_case_owners = similarity_sum_by_owner.sort_values(ascending=False).index.tolist()


        # Return the list of sorted case owners
        return JsonResponse({'sorted_case_owners': sorted_case_owners})