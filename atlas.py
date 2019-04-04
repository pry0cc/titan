import logging
from elasticsearch import Elasticsearch


class Atlas:

    def __init__(self, user, password, url, verify_credentials=False, debug=False):
        self._logger = self._get_logger()
        self._is_debug = debug

        self.doc_type = 'credential'
        self.user = user
        self.password = password

        es_ip = url
        es_port = 443

        self._es = Elasticsearch(
            [es_ip],
            port=es_port,
            http_auth=(user, password)
        )

        if verify_credentials:
            self.validate_connection()

        self.available_indices = self.get_available_indices()

        if self._is_debug:
            self._log('Available Indices:')
            self._log(self.available_indices)


    def _log(self, message, level=logging.DEBUG):
        # If debug log everything
        if self._is_debug:
            self._logger.log(level=level, msg=message)
        # If debug is false but it's an error print it anyway
        elif not self._is_debug and level == logging.ERROR:
            self._logger.log(level, message)
        else:
            return


    def get_available_indices(self):
        # Get all of the index names that are not system ('.') indices
        # Also exclude searchguard index
        return [index_name for index_name
                in self._es.indices.get_alias("*") if '.' not in index_name and 'searchguard' not in index_name]


    def validate_connection(self):
        try:
            # Due to permissions in SearchGuard we cannot allow users to ping
            # therefore we verify the existence of any index as all are protected
            # by authentication. If true, authentication was successful else fails.
            if self._es.indices.exists(index='*'):
                self._log("Credentials validated.")
                return True
            else:
                raise ValueError("Connection failed. Please check credentials.")
        except ValueError as e:
            self._log('Invalid credentials. Please check username and password and try again.', level=logging.ERROR)
        except Exception as e:
            self._log('Error connecting to the ES server.', level=logging.ERROR)


    def search_all_fields(self, value, analyze_wildcard=False, size=100):
        """Searches all available fields in all credential indices"""
        search_body = {
            "size": size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": value,
                                "analyze_wildcard": analyze_wildcard,
                                "default_field": "*"
                            }
                        }
                    ]
                }
            }
        }
        return self._es.search(index=self._get_searchable_indices_joined(),
                               doc_type=self.doc_type,
                               body=search_body)


    def _get_searchable_indices_joined(self):
        return ",".join(self.available_indices)


    def search_email_addresses(self, email_address, size=100):
        """Searches all available indexes for email addresses matching the input"""
        search_body = {
            "size": size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": email_address,
                                "default_field": "emailAddress"
                            }
                        },
                        {
                            "match_phrase": {
                                "emailAddress": {
                                    "query": email_address
                                }
                            }
                        }]
                }
            }
        }
        return self._es.search(index=self._get_searchable_indices_joined(),
                               doc_type=self.doc_type,
                               body=search_body)


    def search_passwords(self, password, size=100):
        """Searched all available documents for matching passwords"""
        search_body = {
            "size": size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": password,
                                "default_field": "password"
                            }
                        },
                        {
                            "match_phrase": {
                                "password": {
                                    "query": password
                                }
                            }
                        }]
                }
            }
        }
        return self._es.search(index=self._get_searchable_indices_joined(),
                               doc_type=self.doc_type,
                               body=search_body)


    def _get_logger(self):
        logger = logging.getLogger('Atlas')
        logger.setLevel(logging.DEBUG)
        logging.basicConfig(
            format=logging.basicConfig(format='[%(levelname)s] @ %(asctime)s : %(message)s', level=logging.DEBUG))
        return logger
