import os
import re
from xml.dom import minidom
from dateutil.parser import parse


class NfoDescriptorFile:
    nfo_file_path = None
    nfo_movie = None

    def __init__(self, nfo_file_path):
        self.nfo_file_path = nfo_file_path
        if not os.path.isfile(self.nfo_file_path):
            raise FileNotFoundError("NFO file does not exist! %s", self.nfo_file_path)

        with open(self.nfo_file_path, "r", encoding="utf-8") as file:
            nfo_data = minidom.parseString(file.read().replace("&", "&amp;"))
        movies = nfo_data.getElementsByTagName('movie')
        if movies:
            self.nfo_movie = movies[0]
        else:
            episodedetails = nfo_data.getElementsByTagName('episodedetails')
            if episodedetails:
                self.nfo_episodedetails = episodedetails[0]
            else:
                raise ValueError("NFO file does not contain a movie or episodedetails element! %s", self.nfo_file_path)

    def get_id(self, default=None):
        if self.nfo_movie:
            return self.get_unique_root_element_value('id', default)
        return self.get_unique_root_element_value('uniqueid', default)

    def get_title(self, default=None):
        return self.get_unique_root_element_value('title', default)

    def get_sort_title(self, default=None):
        return self.get_unique_root_element_value('sorttitle', default)

    def get_original_title(self, default=None):
        return self.get_unique_root_element_value('originaltitle', default)

    def get_tagline(self, default=None):
        return self.get_unique_root_element_value('tagline', default)

    def get_plot(self, default=None):
        return self.get_unique_root_element_value('plot', default)

    def get_outline(self, default=None):
        return self.get_unique_root_element_value('outline', default)

    def get_year(self, default=None):
        if self.nfo_movie:
            return int(self.get_unique_root_element_value('year', default))
        return int(self.get_unique_root_element_value('season', default))

    def get_mpaa(self, default=None):
        # <mpaa>DK:A</mpaa>
        return self.get_unique_root_element_value('mpaa', default)

    def get_certification(self, default=None):
        # <certification>DK:A</certification>
        return self.get_unique_root_element_value('certification', default)

    def get_studio(self, default=None):
        return str(self.get_unique_root_element_value('studio', default))

    def get_premiered(self, default=None):
        parsed_date = default
        try:
            if self.nfo_movie:
                date_str = str(self.get_unique_root_element_value('premiered', default))
            else:
                date_str = str(self.get_unique_root_element_value('aired', default))
            parsed_date = parse(date_str)
        except:
            pass
        return parsed_date

    def get_releasedate(self, default=None):
        parsed_date = default
        try:
            if self.nfo_movie:
                date_str = str(self.get_unique_root_element_value('releasedate', default))
            else:
                date_str = str(self.get_unique_root_element_value('aired', default))
            parsed_date = parse(date_str)
        except:
            pass
        return parsed_date

    def get_runtime(self, default=0):
        return int(self.get_unique_root_element_value('runtime', default))

    def get_most_voted_rating(self, default=0.0):
        rating_value = default
        rating_votes = 0
        ratings = self.get_unique_root_element('ratings')
        for rating in ratings:
            votes = rating.getElementsByTagName('votes')[0].firstChild.data
            votes = int(str(votes).strip())
            if (votes > rating_votes):
                rating_votes = votes
                value = rating.getElementsByTagName('value')[0].firstChild.data
                rating_value = float(str(value).strip())

        return rating_value

    def get_credits(self):
        director_list = []
        directors = self.get_unique_root_element('credits')
        for director in directors:
            name = str(director.firstChild.data).strip()
            director_list.append(name)

        return director_list

    def get_directors(self):
        director_list = []
        directors = self.get_unique_root_element('director')
        for director in directors:
            name = str(director.firstChild.data).strip()
            director_list.append(name)

        return director_list

    def get_genres(self):
        genre_list = []
        genres = self.get_unique_root_element('genre')
        for genre in genres:
            name = str(genre.firstChild.data).strip()
            genre_list.append(name)

        return genre_list

    def get_countries(self):
        country_list = []
        countries = self.get_unique_root_element('country')
        for country in countries:
            name = str(country.firstChild.data).strip()
            country_list.append(name)

        return country_list

    def get_sets(self):
        set_list = []
        sets = self.get_unique_root_element('set')
        for collectionset in sets:
            try:
                setname = collectionset.getElementsByTagName('name')[0].firstChild.data
                setname = str(setname).strip()
                set_list.append(setname)
            except:
                pass

        return set_list

    def get_actors(self):
        actor_list = []
        actors = self.get_unique_root_element('actor')
        for actor in actors:
            try:
                actor_item = {
                    "name": "",
                    "role": "",
                    "thumb": "",
                    "profile": "",
                    "tmdbid": ""
                }
                if actor.getElementsByTagName('name')[0].firstChild:
                    actor_item["name"] = str(actor.getElementsByTagName('name')[0].firstChild.data).strip()
                if actor.getElementsByTagName('role')[0].firstChild:
                    actor_item["role"] = str(actor.getElementsByTagName('role')[0].firstChild.data).strip()
                if actor.getElementsByTagName('thumb')[0].firstChild:
                    actor_item["thumb"] = str(actor.getElementsByTagName('thumb')[0].firstChild.data).strip()
                if actor.getElementsByTagName('profile')[0].firstChild:
                    actor_item["profile"] = str(actor.getElementsByTagName('profile')[0].firstChild.data).strip()
                if actor.getElementsByTagName('tmdbid')[0].firstChild:
                    actor_item["tmdbid"] = str(actor.getElementsByTagName('tmdbid')[0].firstChild.data).strip()
                actor_list.append(actor_item)
            except:
                pass

        return actor_list

    def get_unique_root_element_value(self, tagname, default=None):
        try:
            node = self.get_unique_root_element(tagname)
            nodezero = node[0].firstChild
            value = str(nodezero.data).strip()
        except:
            value = default

        return value

    def get_unique_root_element(self, tagname):
        if self.nfo_movie:
            return self.nfo_movie.getElementsByTagName(tagname)
        return self.nfo_episodedetails.getElementsByTagName(tagname)

    def __str__(self):
        # return string with all get methods
        ret = "NfoDescriptorFile: %s" % self.nfo_file_path + os.linesep
        ret += "Id: %s" % self.get_id() + os.linesep
        ret += "Title: %s" % self.get_title() + os.linesep
        ret += "Sort Title: %s" % self.get_sort_title() + os.linesep
        ret += "Original Title: %s" % self.get_original_title() + os.linesep
        ret += "Tagline: %s" % self.get_tagline() + os.linesep
        ret += "Plot: %s" % self.get_plot() + os.linesep
        ret += "Outline: %s" % self.get_outline() + os.linesep
        ret += "Year: %s" % self.get_year() + os.linesep
        ret += "MPAA: %s" % self.get_mpaa() + os.linesep
        ret += "Certification: %s" % self.get_certification() + os.linesep
        ret += "Studio: %s" % self.get_studio() + os.linesep
        ret += "Premiered: %s" % self.get_premiered() + os.linesep
        ret += "Releasedate: %s" % self.get_releasedate() + os.linesep
        ret += "Runtime: %s" % self.get_runtime() + os.linesep
        ret += "Most Voted Rating: %s" % self.get_most_voted_rating() + os.linesep
        ret += "Credits: %s" % self.get_credits() + os.linesep
        ret += "Directors: %s" % self.get_directors() + os.linesep
        ret += "Genres: %s" % self.get_genres() + os.linesep
        ret += "Countries: %s" % self.get_countries() + os.linesep
        ret += "Sets: %s" % self.get_sets() + os.linesep
        ret += "Actors: %s" % self.get_actors() + os.linesep
        return ret
