# Architect

- [Architect](#architect)
  - [SuiteScript](#suitescript)
  - [App](#app)
    - [Firestore](#firestore)
    - [Tiki](#tiki)

## SuiteScript

NetSuite Records are integrated using REST API specs. Details can be found on **Postman**.

- Methods:
  - `GET`: Get a Record
  - `POST`: Create a Record
  - `DELETE`: Soft delete a Record (Close)
- Response Statuses:
  - `200`: Success
  - `400`: Not Found
  - `>400`: Failure

## App

App is built upon MVC architecture, using **Cloud Function/Functions Framework** as runtime.

The app follows Functional Programming Paradigm.

### Firestore

Stateful data (Tiki ack_ids, etc) are stored in **Firestore** NoSQL.

### Tiki

Tiki utilises `Event Queue API`, polling data at a specified frequency. Upon receving events, the App will call `Resources API` to get details.
