from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from dotenv import load_dotenv
import os


def main():
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        # Get configuration settings
        load_dotenv()
        endpoint = os.getenv("DOC_INTELLIGENCE_ENDPOINT")
        key = os.getenv("DOC_INTELLIGENCE_KEY")
        model_id = os.getenv("MODEL_ID")

        # List available files in sample-forms folder
        forms_dir = "/Users/BryantItonyo1/Desktop/ms-ai-demos/mslearn-ai-information-extraction/Labfiles/03-document-intelligence/custom/sample-forms"
        supported = ('.jpg', '.jpeg', '.png', '.pdf', '.tiff', '.bmp')
        files = [f for f in os.listdir(forms_dir) if os.path.isfile(os.path.join(forms_dir, f)) and f.lower().endswith(supported)]

        if not files:
            print("No files found in sample-forms folder.")
            return

        # Show available files and ask user to choose
        print("\nAvailable forms:")
        for i, file in enumerate(files):
            print(f"  {i + 1}. {file}")

        choice = input("\nEnter the number of the file to analyze: ")
        selected_file = files[int(choice) - 1]
        file_path = os.path.join(forms_dir, selected_file)
        print(f"\nAnalyzing: {selected_file}")

        # Create the client
        document_analysis_client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        # Analyze the selected document
        with open(file_path, "rb") as f:
            poller = document_analysis_client.begin_analyze_document(
                model_id,
                f.read(),
                content_type="application/octet-stream"
            )

        result = poller.result()
        for idx, document in enumerate(result.documents):
            print("--------Analyzing document #{}--------".format(idx + 1))
            print("Document has type {}".format(document.doc_type))
            print("Document has confidence {}".format(document.confidence))
            print("Document was analyzed by model with ID {}".format(result.model_id))
            for name, field in document.fields.items():
                field_value = field.get("valueString") or field.get("content", "N/A")
                print("Found field '{}' with value '{}' and with confidence {}".format(name, field_value, field.get("confidence")))

        print("-----------------------------------")

    except Exception as ex:
        print(ex)

    print("\nAnalysis complete.\n")


if __name__ == "__main__":
    main()