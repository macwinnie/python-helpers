#!/usr/bin/env python3

import requests, os, json, gc, getpass

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By


class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, status, url):
        self.status = status
        self.url = url

    def __str__(self):
        return "APIError: status={}\nURL:      {}".format(self.status, self.url)


class Browser:
    """Base browser for Selenium assisted applications"""

    browser = None
    cookies = {}
    app = {}
    lastUrl = ""
    sessionBaseHeaders = None

    appInfo = {}

    def __init__(self):
        """function to initiate the systems as needed"""
        # fetch variables from ENV
        from dotenv import load_dotenv

        load_dotenv()
        # ignore warnings, when SSL_IGNORE is set to true
        import os

        if os.getenv("SSL_IGNORE", "False").lower() in ["1", "true", "t", "y", "yes"]:
            import urllib3

            urllib3.disable_warnings()
        # gather App info and start browser
        self.gatherAppInfo()
        self.startBrowser()

    def setCookies(self, cookieDict, url=None, returnSession=False, curl=True):
        """helper function to set cookies on browser"""
        if url == None:
            url = self.app["url"]
        # parsedUrl = urllib.parse.urlparse(url)
        # domain, path = [ parsedUrl.netloc, parsedUrl.path ]
        # if path == '':
        #     path = '/'
        self.browser.get(url)
        for key, value in cookieDict.items():
            if os.getenv("PRINT_DEBUG_INFO", "False").lower() in ["1", "true", "t", "y", "yes"]:
                print("Cookie is being set:")
                print({"key": key, "value": value})
                print()
            # # does no more work since Python / Selenium Cookies can only be set for loaded URLs anymore ...
            # self.browser.add_cookie( { "name": key, "value": value, "domain": domain, "path": path } )
            self.browser.add_cookie({"name": key, "value": value})
        self.browser.refresh()
        if returnSession:
            return self.toSession(curl=curl)

    def loadCookies(self, givenCookies=None, url=None):
        """function to load cookies from JSON string ENV variable `COOKIES` – or a given Python dictionary"""
        if givenCookies == None:
            givenCookies = json.loads(os.getenv("COOKIES", "{}"))
        if len(givenCookies) > 0:
            self.setCookies(givenCookies, url)

    def gatherAppInfo(self):
        """
        function to set application information

        each `appInfo` has to be a dictionary with the following keys:
          * `env` (MANDATORY – name of the corresponding environmental variable)
          * `description` (MANDATORY – if the user is asked to enter the value, this information is shown)
          * `password` (OPTIONAL – default `False`; if set `True`, the potential user input is hidden)
          * `url` (OPTIONAL – default `False`; if set `True`, the `urlLastChar` is ensured to be last part of the value)
          * `urlLastChar` (OPTIONAL – default `/`)
          * `default` (OPTIONAL – default value for the app information; if set, the user won't be able to input the information)
        `appInfo` itself is also a dictionary and the key `url` is mandatory, the keys `user` and `passwd` are highly recommended.
        """
        self.app = {}
        for key, config in self.appInfo.items():
            value = None
            # relevant for asking for a password
            if "password" not in config:
                config["password"] = False
            # relevant for formatting urls
            if "url" not in config:
                config["url"] = False
            # relevant for formatting urls
            if "urlLastChar" not in config:
                config["urlLastChar"] = "/"
            # relevant if there is a default value for this
            # setting in the specific browser
            if "default" not in config:
                config["default"] = None
            # check for config
            if "env" in config:
                value = os.getenv(config["env"], config["default"])
            # ensure value not None
            if value == None:
                # ask for user input
                if config["password"]:
                    value = getpass.getpass("{d}: ".format(d=config["description"]))
                else:
                    value = input("{d}: ".format(d=config["description"]))
            # adjust url
            if (
                config["url"]
                and len(config["urlLastChar"]) > 0
                and value[-1] != config["urlLastChar"]
            ):
                value += config["urlLastChar"]
            # set value to app array
            self.app[key] = value

    def startBrowser(self, custom_capabilities={}):
        """Start Selenium browser"""
        btype = os.getenv("SELENIUM_BROWSER_TYPE", "FIREFOX")
        gridUrl = os.getenv("SELENIUM_GRID")

        if btype.lower() in ["chrome"]:
            capabilities = DesiredCapabilities.CHROME.copy()
        elif btype.lower() in ["opera"]:
            capabilities = DesiredCapabilities.OPERA.copy()
        elif btype.lower() in ["safari"]:
            capabilities = DesiredCapabilities.SAFARI.copy()
        else:
            capabilities = DesiredCapabilities.FIREFOX.copy()

        if os.getenv("SSL_IGNORE", "False").lower() in ["1", "true", "t", "y", "yes"]:
            capabilities["acceptInsecureCerts"] = True

        for key, value in custom_capabilities.items():
            capabilities[key] = value

        self.browser = webdriver.Remote(command_executor=gridUrl, desired_capabilities=capabilities)
        self.browser.set_script_timeout(os.getenv("SELENIUM_TIMEOUT", 30000))

    def checkElementByXpath(self, xpath):
        """helper function to check if element (XPATH) exists on page"""
        try:
            self.browser.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return False
        return True

    def checkElementByID(self, ident):
        """helper function to check if element (ID) exists on page"""
        try:
            self.browser.find_element(By.ID, ident)
        except NoSuchElementException:
            return False
        return True

    def sessionPostRequest(
        self,
        url,
        data,
        transferCookies=False,
        headers=None,
        curl=True,
        session=None,
        urlOverride=False,
    ):
        """helper function to send POST request"""
        if session == None:
            session = self.toSession(curl=curl)
        headers = self.appendSessionHeaders(headers)
        if headers is not None:
            request = session.post(url, data=data, headers=headers)
        else:
            request = session.post(url, data=data)
        if transferCookies:
            # write Cookies from POST request to Selenium Browser
            new_cookies = session.cookies.get_dict()
            if urlOverride:
                self.get(url, login=False)
                self.setCookies(new_cookies, url=url)
            else:
                self.get(request.url, login=False)
                self.setCookies(new_cookies, url=request.url)
            self.refresh()
        return request

    def sessionPutRequest(
        self, url, data, transferCookies=False, headers=None, curl=True, session=None
    ):
        """helper function to send PUT request"""
        if session == None:
            session = self.toSession(curl=curl)
        headers = self.appendSessionHeaders(headers)
        if headers is not None:
            request = session.put(url, data=data, headers=headers)
        else:
            request = session.put(url, data=data)
        if transferCookies:
            # write Cookies from POST request to Selenium Browser
            new_cookies = session.cookies.get_dict()
            self.get(request.url, login=False)
            self.setCookies(new_cookies)
            self.refresh()
        return request

    def sessionGetRequest(self, url, transferCookies=False, headers=None, curl=True, session=None):
        """helper function to send GET request"""
        if session == None:
            session = self.toSession(curl=curl)
        headers = self.appendSessionHeaders(headers)
        if headers is not None:
            request = session.get(url, headers=headers)
        else:
            request = session.get(url)
        if transferCookies:
            # write Cookies from POST request to Selenium Browser
            new_cookies = session.cookies.get_dict()
            self.get(request.url, login=False)
            self.setCookies(new_cookies)
            self.refresh()
        return request

    def apiGetInfo(self, apiUrl, returnResponse=False, session=None, curl=True):
        """Function to gather information from API URL – if `returnResponse` is True, the whole request response is returned, otherwise only the decoded answer object"""
        if session == None:
            session = self.toSession(curl=curl)
        rsp = session.get(apiUrl)
        if returnResponse:
            return rsp
        else:
            if rsp.status_code == 200:
                return json.loads(rsp.text)
            elif rsp.status_code == 404:
                return None
            else:
                raise Exception(
                    "Error while API fetch:\n======================\n\nResponse Code: {rc}\n\n{body}".format(
                        rc=rsp.status_code, body=rsp.text
                    )
                )

    def appendSessionHeaders(self, headers=None):
        """append session headers and retrieve them"""
        if headers is None:
            return self.sessionBaseHeaders
        else:
            for k, v in self.sessionBaseHeaders.items():
                if k not in headers:
                    headers[k] = v
            return headers

    def restoreCookies(self):
        """Restore cookies on Browser"""
        for cookie in self.cookies:
            self.browser.add_cookie(cookie)

    def renew(self):
        """Renew browser by closing and reopening it with restored Cookies"""
        try:
            self.browser.quit()
        except:
            pass
        self.startBrowser()
        self.browser.get(self.lastUrl)
        self.restoreCookies()

    def refresh(self):
        """Reload page in Browser"""
        currentUrl = self.browser.current_url
        self.get(currentUrl)
        # self.browser.refresh() # bricks sessionPostRequest calls ...

    def get(self, url, login=True):
        """Get url in Browser"""
        self.browser.get(url)
        if login and not self.checkLogin():
            self.login()
            self.browser.get(url)
        self.cookies = self.browser.get_cookies()
        self.lastUrl = url
        gc.collect()

    def toSession(self, curl=False):
        """Return python session"""
        sessionObj = requests.session()
        if curl:
            agent = "curl/7.54"
        else:
            agent = self.browser.execute_script("return navigator.userAgent")
        sessionObj.headers = {"User-Agent": agent}
        if len(self.cookies) > 0:
            for c in self.cookies:
                sessionObj.cookies.set(c["name"], c["value"])
        if os.getenv("SSL_IGNORE", "False").lower() in ["1", "true", "t", "y", "yes"]:
            sessionObj.verify = False
        return sessionObj

    def toSoup(self):
        """get BeautifulSoup representation of currently loaded page"""
        return BeautifulSoup(self.browser.page_source, "html.parser")

    def __del__(self):
        """magic function to close the browser instance"""
        self.browser.quit()
