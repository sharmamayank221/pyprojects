import googleapiclient.discovery as discovery
from httplib2 import Http
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import json
from datetime import date

SCOPES = 'https://www.googleapis.com/auth/documents.readonly'
DISCOVERY_DOC = 'https://docs.googleapis.com/$discovery/rest?version=v1'
DOCUMENT_ID = '1YQppOerDW0ijZ1fsDZrXjcS3gKf3SF2YEPA6ehsijb8'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth 2.0 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    store = file.Storage('token.json')
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        credentials = tools.run_flow(flow, store)
    return credentials

def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')
    if not text_run:
        return ''
    return text_run.get('content')

def read_title(doc):
    """Reads the title of the document."""
    title = doc.get('title')
    return title

def read_structural_elements(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """
    text = ''
    is_desired_section = False  # Flag to indicate when the desired section starts
    outline_started = False  # Flag to indicate if the outline section has started

    for value in elements:
        if 'paragraph' in value:
            paragraph_elements = value.get('paragraph').get('elements')
            for elem in paragraph_elements:
                text_run = elem.get('textRun')
                if text_run:
                    content = text_run.get('content')
                    if outline_started:
                        # Stop adding content when the outline section is encountered
                        if content.strip() == "":
                            outline_started = False
                            is_desired_section = True  # Start adding content after outline
                    elif is_desired_section:
                        # Check if the content is part of the desired section
                        if content.strip() != "":
                            text += content + '\n'
                    elif content.strip() == "Outline":
                        # Start adding content when the desired section is encountered
                        outline_started = True

    return text.strip()








def read_outline(elements):
    """Reads the outline part of the document."""
    outline_text = ''
    is_outline_started = False

    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                if 'textRun' in elem:
                    content = elem.get('textRun').get('content')
                    if content.strip() == "Outline":
                        is_outline_started = True
                        continue
                    if is_outline_started:
                        outline_text += content.strip() + "\n"
    return outline_text.strip()

def read_meta_description(doc):
    """Reads the meta description from the document if available, otherwise provides an empty string."""
    meta_description = ""
    body_content = doc.get('body').get('content')
    is_meta_section = False
    for element in body_content:
        if 'paragraph' in element:
            elements = element.get('paragraph').get('elements')
            for elem in elements:
                if 'textRun' in elem:
                    content = elem.get('textRun').get('content')
                    if is_meta_section:
                        if content.strip() == "":
                            # Stop reading if encountering an empty line
                            is_meta_section = False
                        else:
                            # Concatenate content until the end of the section
                            meta_description += content.strip() + " "
                    elif content.strip().startswith("Meta:"):
                        # Start capturing content after encountering "Meta:"
                        is_meta_section = True
        elif 'tableOfContents' in element:
            # Break the loop if we reach the table of contents
            break
    return meta_description.strip()








def read_table_of_contents(doc):
    """Reads the table of contents from the document based on the headings."""
    table_of_contents = ''
    body_content = doc.get('body').get('content')
    seen_headings = set()
    for element in body_content:
        if 'paragraph' in element:
            elements = element.get('paragraph').get('elements')
            for elem in elements:
                if 'textRun' in elem:
                    content = elem.get('textRun').get('content')
                    if content.strip().startswith("Outline"):
                        continue  # Skip the "Outline" section itself
                    elif content.strip().startswith(("About", "The Current State", "The Impact", "Exploring", "The Pros", "Navigating", "Commercial", "Tips", "Trends", "The Role")):  # Start of a new heading
                        if content.strip() not in seen_headings:
                            table_of_contents += content.strip() + "\n"
                            seen_headings.add(content.strip())
                    elif content.strip().startswith("Recap and Future Outlook"):
                        table_of_contents += content.strip() + "\n"  # Include "Recap and Future Outlook" in the table of contents
                        return table_of_contents.strip()  # Exit the function once "Recap and Future Outlook" is found
    return table_of_contents.strip()

def main():
    """Uses the Docs API to save the text of a document as JSON."""
    credentials = get_credentials()
    http = credentials.authorize(Http())
    docs_service = discovery.build(
        'docs', 'v1', http=http, discoveryServiceUrl=DISCOVERY_DOC)
    doc = docs_service.documents().get(documentId=DOCUMENT_ID).execute()
    doc_title = read_title(doc)
    doc_content = read_structural_elements(doc.get('body').get('content'))
    doc_outline = read_outline(doc.get('body').get('content'))

    # Additional metadata
    alt = "Discover the top real estate investing opportunities in Deltona, for 2024."  # Using alt from the document as main image name
    date_published = str(date.today())  # Today's date
    category = "Real Estate"
    order = 63  # Example order

    # Extracting meta-description from the document
    meta_description = read_meta_description(doc)

    # Extracting table of contents from the document
    table_of_contents = read_table_of_contents(doc)
      # Convert table of contents to HTML unordered list format
    table_of_contents = "<ul id=''>" + "".join([f"<li>{item.strip()}</li>" for item in table_of_contents.split("\n")]) + "</ul><p>‍</p>"
    
     # Generate slug with single dashes
    slug = doc_title.lower().replace(" ", "-").replace(",", "")
    slug = slug.replace("--", "-")  # Replace double dashes with single dashes

    # Create a dictionary to store the content
    content_dict = {
        "fieldData": {
            "name": doc_title,
            "meta-title": doc_title,
            "meta-description": meta_description,
            "main-image-name": alt,
            "date-published": date_published,
            "category": category,
            "order": order,
            "table-of-contents": table_of_contents,
            "content": doc_content,
            "slug": slug,
            "author" : "Tirios Team",
            "blog-image": {
                "fileId": "661c98dbf65ac12434cedb19",
                "url": "https://uploads-ssl.webflow.com/636dab449b355b7631457f3e/661c98dbf65ac12434cedb19_MiamiBeach-min.png",
                "alt": None
            },
            "author-image": {
                "fileId": "65fd013b82c9e08915e384bc",
                "url": "https://uploads-ssl.webflow.com/636dab449b355b7631457f3e/65ce39b0c334f65007e4c7c8_tirios-icon.png",
                "alt": None
            }
        }
    }

    # Save the content as JSON
    with open('document_content.json', 'w') as json_file:
        json.dump(content_dict, json_file, indent=4)

    print("Document content saved as JSON.")

if __name__ == '__main__':
    main()
