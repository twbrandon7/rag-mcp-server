# Project Requirements Document

## **1. Introduction & Overview**

This Project Requirements Document (PRD) outlines the functional requirements for the Web Content Vectorization Service. This application allows users to organize their submitted URLs into "projects," which are then crawled, their content transformed into vector embeddings using a transformer model, and stored in a vector database (pgvector). The service also includes robust user authentication and ensures data privacy and project-based sharing.

## **2. User Authentication & Account Management**

This section details how users can register, log in, and manage their access to the service, including various authentication methods and account linking.

| **Requirement ID** | **Description** | **User Story** | **Expected Behavior/Outcome** |
| --- | --- | --- | --- |
| FR010 | User Authentication (Google) | As a user, I want to be able to log in using my Google account so I can securely access my data. | The system should integrate with Google's OAuth 2.0 for user authentication, allowing users to sign in with their existing Google credentials. Upon successful login, the user should be redirected to their personalized dashboard. |
| FR011 | User Authentication (Microsoft) | As a user, I want to be able to log in using my Microsoft account so I can securely access my data. | The system should integrate with Microsoft's authentication services (e.g., Azure AD or Microsoft Account) for user authentication, allowing users to sign in with their existing Microsoft credentials. Upon successful login, the user should be redirected to their personalized dashboard. |
| FR014 | Account Registration (Email/Password) | As a new user, I want to be able to create an account using my email and a password so I can access the service. | The system should provide a registration form where users can enter their email address and a chosen password. Upon successful submission, a new user account should be created, and the user should be logged in or prompted to log in. |
| FR015 | Account Linking (SSO & Email/Password) | As a user, if I log in with Google or Microsoft and my email matches an existing email/password account, I want these accounts to be linked so I can use either method to log in later. | When a user logs in via Google or Microsoft SSO, the system should check if an existing email/password account with the same email address exists. If a match is found, the accounts should be linked, allowing subsequent logins via either SSO or email/password. |

## **3. Project Management**

This section outlines the functionality for users to create, organize, and manage their projects, which serve as containers for their collected links and vectorized content.

| **Requirement ID** | **Description** | **User Story** | **Expected Behavior/Outcome** |
| --- | --- | --- | --- |
| FR017 | Creating a New Project | As a user, I want to create a new project so I can group related links and their vectorized content. | The system should provide a clear interface (e.g., a "Create New Project" button) allowing users to define a name for their project. Upon creation, an empty project should be available to which URLs can be added. |

## **4. URL Submission & Processing**

This section details the user-facing features for submitting URLs *within the context of a project*, and the initial steps the system takes to process them, including status tracking and handling common submission issues.

| **Requirement ID** | **Description** | **User Story** | **Expected Behavior/Outcome** |
| --- | --- | --- | --- |
| FR001 | Submitting a Single URL to a Project | As a user, I want to be able to input a single URL into a selected project so that its content can be processed and associated with that project. | The system should provide a dedicated input field for entering a single URL within the context of an active or selected project. Upon submission, the URL should be added to the processing queue and linked to the specified project. |
| FR002 | Submitting Multiple URLs to a Project | As a user, I want to be able to submit multiple URLs at once (e.g., via a list or bulk paste) into a selected project to process several webpages efficiently and associate them with that project. | The system should provide a text area or a file upload option where users can enter or paste multiple URLs, one per line, within the context of an active or selected project. Upon submission, all valid URLs should be added to the processing queue and linked to the specified project. |
| FR003 | Initiating Content Crawling | As a user, I want the system to automatically trigger a crawler for submitted URLs so that webpage content can be retrieved. | Upon successful submission of a URL, the backend system should automatically initiate a web crawler to fetch the content of the specified webpage. |
| FR004 | Displaying Processing Status | As a user, I want to view the real-time status of my submitted URLs (e.g., "Pending," "Crawling," "Encoding," "Stored," "Failed"). | The system should display a list or dashboard showing each submitted URL along with its current processing status. Status updates should be reflected promptly. |
| FR005 | Handling Crawling Failures | As a user, I want to be notified if a URL cannot be crawled (e.g., due to a broken link, server error, or robots.txt restrictions). | If the crawler fails to retrieve content from a URL, its status should change to "Failed," and a clear error message explaining the reason should be provided. |
| FR008 | Preventing Duplicate URL Processing | As a user, I want the system to recognize and prevent re-processing of URLs that have already been successfully stored. | If a user submits a URL that has already been successfully processed and stored, the system should inform the user that it's a duplicate and not initiate a new processing cycle for it. |

## **5. Content Vectorization & Storage**

This section focuses on the core backend processes of the service: extracting, transforming, and storing webpage content as vector embeddings in the database, ensuring association with the correct project.

| **Requirement ID** | **Description** | **User Story** | **Expected Behavior/Outcome** |
| --- | --- | --- | --- |
| FR006 | Content Encoding by Transformer Model | As a user, I expect the crawled webpage content to be encoded into vectors using a transformer model. | After successful crawling, the system should automatically pass the extracted text content through a pre-configured transformer model to generate a vector embedding. |
| FR007 | Storing Vectors in Database | As a user, I expect the generated content vectors to be stored in a vector database (pgvector). | Upon successful encoding, the system should split the webpage content into multiple chunks. For each chunk, it should store its original content, its associated vector embedding, and a reference to the source webpage and its project in the pgvector database. |

## **6. Data Access & Management**

This section covers how users can view and potentially manage their projects, URLs, and their associated processed data, including retrieval by an LLM.

| **Requirement ID** | **Description** | **User Story** | **Expected Behavior/Outcome** |
| --- | --- | --- | --- |
| FR009 | Displaying Projects and their Processed URLs | As a user, I want to see a list of my projects, and within each project, a list of all URLs that have been successfully crawled, encoded, and stored. | The system should provide a view displaying all user-created projects. Each project should be selectable, revealing a list of URLs within that project that have reached the "Stored" status, possibly with timestamps. |
| FR016 | LLM Content Retrieval (MCP Server) | As a user, I want an LLM (via an MCP server) to be able to query my stored content from one or more specified projects and retrieve relevant original content based on the query. | The system should expose an API endpoint (via the MCP server) that allows an LLM to submit a query along with one or more project identifiers. The MCP server should then perform a similarity search against the user's stored vector embeddings *within the specified projects* in pgvector and return the original content of the most relevant chunks. |

## **7. Security & Privacy**

This section addresses the critical aspects of data security, ensuring that user-submitted data and projects remain private by default and can only be accessed or shared under explicit user control.

| **Requirement ID** | **Description** | **User Story** | **Expected Behavior/Outcome** |
| --- | --- | --- | --- |
| FR012 | Private Project Access | As a user, I want to ensure that only I can view my projects, including the links and vectors within them, unless I explicitly share a project. | The system must enforce strict access control, ensuring that each user's projects, and all associated URLs, crawled content, and generated vectors, are private by default and only accessible by the authenticated user who created them. |
| FR013 | Project Sharing Mechanism | As a user, I might want to share an entire project, including all its links and associated vectors, with other users or the public. | The system should provide a mechanism (e.g., a share button or link generation at the project level) that allows users to selectively share their processed projects. |