"""Module to handle registering routes and handlers """
import re
from typing import Callable, Any
from app.messages import HTTPRequestMethod
from app.handlers import HTTPHandler


class Router:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, HTTPRequestMethod], HTTPHandler] = {}

    def register(self, path: str, method: HTTPRequestMethod):
        """Decorator to register handler for given path patterns.

           Handlers ALWAYS expect params as the first arg
           Handler can take params from path /foo/{bar} like so:

           @Router.register("/foo/{bar}", HTTPRequestMethod.GET)
           def handler(params dict[str, Any], r: HTTPRequestMethod) -> HTTPResponse:
                print(params["bar"])
           
        """
        def inner(func: HTTPHandler) -> HTTPHandler:
            normalized = self._normalize(path)
            self._routes[(normalized, method)] = func
            return func
        return inner
    
    def resolve(self, path: str, req_method: HTTPRequestMethod) -> tuple[Callable, dict] | None:
        """Attempt to resolve a path to a registered handler and params. Returns callable and corresponding params."""
        normalized = self._normalize(path)

        for pattern_method_tup, func in self._routes.items():
            pattern, method = pattern_method_tup # Just get the pattern to resolve any params
            resolves, params = self._resolve_params(pattern, normalized)

            if resolves and method == req_method:
                return func, params
        
        return None

            
    def _resolve_params(self, pattern, path: str) -> tuple[bool, dict[str, Any]]:
        """Returns true if path can be resolved and any {params} in a pattern for a given path. Can be {}
           ie. pattern=/foo/{param1} path=/foo/bar -> {param1: bar}
        """

        regex_pattern, param_names = self._compile(pattern)

        # If no params, regex_pattern has no capture groups
        path_resolves = re.fullmatch(regex_pattern, path)

        if not path_resolves:
            return False, {}

        return True, dict(zip(param_names, path_resolves.groups())) # Matches and param names are in same order in path


    def _compile(self, path_pattern: str) -> tuple[str, list[str]]:
        """
        Takes a paramaterised path, extracts the param name and replaces it with a regex search.
        Each regex group in the returning Match will correspond to the index in the List
        ie. /foo/1/bar/2 -> regex=/foo/[(^/)]/bar/[(^/)] param_names=[1, 2] 
        Returns pattern, [] if no {param} in path_pattern
         """
        param_names = []

        def sub_pattern_for_name(match: re.Match):
            param_names.append(match.group(1))
            return r"([^/]+)" # Any character but '/'

        # Escape all special chars and remove '\' infront of curly braces
        # This is so found params can be replaced with a regex pattern for later use
        raw_string = re.escape(path_pattern).replace(r"\{", "{").replace(r"\}", "}")

        # Replace any words in {} with any char but '/' pattern
        regex_param_pattern = re.sub(r"\{(\w+)\}", sub_pattern_for_name, raw_string)

        return regex_param_pattern, param_names


    @staticmethod
    def _normalize(path: str):
        """Removes trailing '/' from paths, is under class mainly for clarity"""
        return "/" + path.strip("/")
    
router = Router()
def get_router() -> Router:
    """Getter for singleton module level Router"""
    return router

def collect_handlers():
    """Importing handlers module registers all handlers"""
    import app.handlers #noqa

