# Financial Query Bot

This is essentially a Retrieval Augmented Genterator (RAG) model that generates sql queries. This program is to help non technical users be able to access MySQL databases. If a user want to query data from a MYSQL database, they can ask the model in English words on what data they want to access and the model reponds to the user by giving the proper SQL query. 

For example: 
- Query: I want all the stocks that have an Opening price greater than 50. 
- Response: SELECT * FROM stock_data WHERE open > 50 