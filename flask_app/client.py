import requests


class GoogleImage(object):
    def __init__(self, serp_json):
        self.position = serp_json["position"]
        self.thumbnail = serp_json["thumbnail"]
        self.title = serp_json["title"]
        self.link = serp_json["link"]
        self.source = serp_json["source"]

    def __repr__(self):
        return self.title


class PicClient(object):
    def __init__(self, api_key):
        self.sess = requests.Session()
        self.base_url = f"https://serpapi.com/search.json?api_key={api_key}&tbm=isch&ijn=0&"

    def search(self, search_string):
        """
        Searches the API for the supplied search_string, and returns
        a list of Media objects if the search was successful, or the error response
        if the search failed.

        Only use this method if the user is using the search bar on the website.
        """
        #payload = {'q': search_string}
        search_string = "+".join(search_string.split())

        search_url = f"q={search_string}"

        resp = self.sess.get(self.base_url + search_url)

        if resp.status_code != 200:
            raise ValueError(
                "Search request failed; make sure your API key is correct and authorized"
            )

        data = resp.json()

        #if not data:
        #    raise ValueError(f'[ERROR]: Error retrieving results: \'{data["Error"]}\' ')

        search_results_json = data["images_results"]
        #remaining_results = int(data["totalResults"])

        result = []

        for item_json in search_results_json:
            result.append(GoogleImage(item_json))

        return result

    def retrieve_movie_by_id(self, imdb_id):
        """
        Use to obtain a Movie object representing the movie identified by
        the supplied imdb_id
        """
        movie_url = self.base_url + f"i={imdb_id}&plot=full"

        resp = self.sess.get(movie_url)

        if resp.status_code != 200:
            raise ValueError(
                "Search request failed; make sure your API key is correct and authorized"
            )

        data = resp.json()

        if data["Response"] == "False":
            raise ValueError(f'Error retrieving results: \'{data["Error"]}\' ')

        movie = Movie(data, detailed=True)

        return movie


## -- Example usage -- ###
if __name__ == "__main__":
    import os

    client = PicClient(os.environ.get("SERP_API_KEY"))

    movies = client.search("coffee")

    for movie in movies:
        print(movie)

    print(len(movies))
