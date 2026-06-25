from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest


def main():
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        # Get config settings
        load_dotenv()
        endpoint = os.getenv('ENDPOINT')
        key = os.getenv('KEY')

        # Set analysis settings
        filePath = "/Users/BryantItonyo1/Desktop/ms-ai-demos/mslearn-ai-information-extraction/Labfiles/03-document-intelligence/prebuilt/sample-invoice/sample-invoice.pdf"
        fileLocale = "en-US"
        fileModelId = "prebuilt-invoice"

        print(f"\nConnecting to Forms Recognizer at: {endpoint}")
        print(f"Analyzing invoice at: {filePath}")

        # Create the client
        document_analysis_client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        # Analyze the invoice
        with open(filePath, "rb") as f:
            poller = document_analysis_client.begin_analyze_document(
                "prebuilt-invoice",
                f.read(),
                locale=fileLocale,
                content_type="application/octet-stream"
            )

        # Display invoice information to the user
        result = poller.result()
        for document in result.documents:
            vendor_name = document.fields.get("VendorName")
            if vendor_name:
                print(f"\nVendor Name: {vendor_name.get('valueString')}, with confidence {vendor_name.get('confidence')}.")
            customer_name = document.fields.get("CustomerName")
            if customer_name:
                print(f"Customer Name: {customer_name.get('valueString')}, with confidence {customer_name.get('confidence')}.")
            invoice_total = document.fields.get("InvoiceTotal")
            if invoice_total:
                amount = invoice_total.get("valueCurrency", {})
                print(f"Invoice Total: {amount.get('currencySymbol', '$')}{amount.get('amount')}, with confidence {invoice_total.get('confidence')}.")

    except Exception as ex:
        print(ex)

    print("\nAnalysis complete.\n")


if __name__ == "__main__":
    main()