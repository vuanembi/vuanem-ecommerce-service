from firestore import DB


def backup(document: str, collection: str):
    for doc in DB.document(document).collection(f"{collection}").get():
        doc_ref = (
            DB.document(document).collection(f"{collection}-backup").document(doc.id)
        )
        doc_ref.set(doc.to_dict())


# backup("Tiki", "Order")
# backup("NetSuite", "PreparedOrder")
# backup("Lazada", "Order")
backup("Shopee", "Order")
