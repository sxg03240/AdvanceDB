from flask import Flask, Response, request, jsonify
import pymongo
import json

app = Flask(__name__)

try:
    mongo = pymongo.MongoClient(
        host="localhost", port=27017, serverSelectionTimeoutMS=1000
    )
    db = mongo.database
    mongo.server_info()  # trigger exception if cannot connect to db
except Exception as ex:
    print(ex)


# GET
# 4. Retrieve all the movies and shows in database
@app.route("/api", methods=["GET"])
def get_all_movies():
    try:
        data = list(db.netflix.find())
        for movie_details in data:
            movie_details["_id"] = str(movie_details["_id"])

        return Response(
            response=json.dumps(data), status=200, mimetype="application/json"
        )


    except Exception as ex:
        print(ex)
    return Response(
        response=json.dumps({"message": "cannot read movies"}),
        status=500,
        mimetype="application/json",
    )


# GET details by title
# 5.Display the movie and show’s detail using title
@app.route("/api/<title>", methods=["GET"])
def get_movie_by_title(title):
    try:
        movie_details = list(db.netflix.find({"title": title}))
        count = len(movie_details)
        if count > 0:
            print(movie_details)
            result = [
                {item: netflix[item] for item in netflix if item != "_id"}
                for netflix in movie_details
            ]
            return jsonify({"result": result})
        else:
            response = Response(
                {"Netflix doesn't have the movie, please see suggestions"}
            )
            return response

    except Exception as ex:
        return Response(
            response=json.dumps(
                {"message": "Netflix doesn't have the movie, please see suggestions"}
            ),
            status=500,
            mimetype="application/json",
        )


# POST
# 1. Insert the new movie and show.
@app.route("/api", methods=["POST"])
def add_movie():
    try:
        movie_details = request.get_json()
        db_response = db.netflix.insert_one(movie_details)
        db.netflix.find_one()
        return Response(
            response=json.dumps(
                {"message": "movie inserted", "id": f"{db_response.inserted_id}"}
            ),
            status=200,
            mimetype="application/json",
        )

    except Exception as ex:

        return Response(
            response=json.dumps({"message": "unable to add the movie"}),
            status=500,
            mimetype="application/json",
        )


# Update/Patch
# 2.Update the movie and show information using title.

@app.route("/api/<title>", methods=["PATCH"])
def update_movie(title):
    _json = request.json
    _imdb_score = _json["imdb_score"]
    _title = _json["title"]
    _description = _json["description"]

    try:
        db.netflix.update_one(
            {"title": title},
            {
                "$set": {
                    "imdb_score": _imdb_score,
                    "title": _title,
                    "description": _description,
                }
            },
        )

        updated_movie = get_movie_by_title(_title)
        return updated_movie

    except Exception as ex:

        return Response(
            response=json.dumps({"message": "Movie is not updated"}),
            status=500,
            mimetype="application/json",
        )


# Delete
# 3.Delete the movie and show information using title.

@app.route("/api/<title>", methods=["DELETE"])
def delete_movie(title):
    try:
        dbresponse = db.netflix.delete_one({"title": title})
        if dbresponse.deleted_count == 1:
            return Response(
                response=json.dumps({"message": "movie deleted", "Title": f"{title}"}),
                status=200,
                mimetype="application/json",
            )
    except Exception as ex:
        return Response(
            response=json.dumps({"message": "Movie not found"}),
            status=500,
            mimetype="application/json",
        )


if __name__ == "__main__":
    app.run(port=80, debug=True)
