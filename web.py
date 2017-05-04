# This program has Copyrigth
# <one line to give the program's name and a brief idea of what it does.>
    #Copyright (C) <year>  <Nicole Vizhnay Corral>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import http.client
import http.server
import socketserver

class OpenFDAHTML():
    def get_main_page(self):
        html="""
        <html>
            <head>
            </head>
            <body>
                <img src="http://www.openbiomedical.org/wordpress/wp-content/uploads/2015/09/openfda_logo.jpg" width="400" height="250" alt="The Scream">
                <form method= "get" action="listDrugs">
                    <input type= "submit" style="color: #003366; background-color: #99CCFF;border-radius:7px; cursor:pointer; box-shadow= 4px 6px 8 px" value="Send to OpenFDA">
                    <span style=”border-image: initial; border: 1px solid blue;”>Limit:</span><input name="number" size='3' type= "text">
                    </input>
                </form>
                <form method= "get" action="searchDrug">
                    <b>Drug name</b> <input type="text" name="drug">
                    <input type="submit" style="color: #003366; background-color: #99CCFF; border-radius:7px;cursor:pointer" value="Send to OpenFDA">
                </form>
                <form method= "get" action="listCompanies">
                    <input type="submit" style="color: #003366; background-color: #99CCFF; border-radius:7px;cursor:pointer" value="Ask companies">
                    Limit: <input name="number" size='3' type= "text">
                </form>
                <form method= "get" action="searchCompany">
                    <b>Company name</b> <input type= "text" name="company">
                    <input type="submit" style="color: #003366; background-color: #99CCFF;border-radius:7px; cursor:pointer"value="Search medicine">
                    </input>
                </form>
                <form method= "get" action= "listGender">
                    <b>Patient sex</b> <input type="submit"  style="color: #003366; background-color: #99CCFF; border-radius:7px; cursor:pointer" value="Search sex">
                    Limit: <input name="number" size='3' type="text">
                </form>
                <for method= "get" action="redirect">
                </form>
                <for method= "get" action="secret">
                </form>
            </body>
        </html>
        """
        return html

    def get_list_html(self,items):
        list_html="""
        <html>
            <head>
                <title>OpenFDA Cool App</title>
            </head>
            <body>
                <ol>
          """

        for item in items:
            list_html+= "<li>" +item+ "</li>\n"

        list_html+= """
                </ol>
                <form method= "get" action= "back">
                    <input type="submit"  style="color: #003366; background-color: #99CCFF; cursor:pointer" value="Come back">
                </form>
            </body>
        </html>
        """
        return list_html

    def get_page_not_found(self):
        html="""
            <html>
              <head>
                 <title>OpenFDA Cool App</title>
              </head>
              <body>
                <h3>Resource not found Error 404</h3>
              </body>
            </html>
          """
        return html

    def get_page_not_correct_limit(self):
        html="""
            <html>
              <head>
                 <title>OpenFDA Cool App</title>
              </head>
              <body>
                <h3>Por favor introduzca un numero correcto en el campo limite</h3>
              </body>
            </html>
          """
        return html

class OpenFDAParser():
    def get_companies_from_events(self,events):
        companies=[]
        for event in events:
            companies = companies + [event["companynumb"]]
        return companies

    def get_drugs_from_events(self,events):
        drugs=[]
        for event in events:
            drugs = drugs + [event["patient"]["drug"][0]["medicinalproduct"]]
        return drugs

    def get_genders_from_events(self,events):
        lista=[]
        for event in events:
            lista= lista + [event["patient"]["patientsex"]]
        return lista


class OpenFDAClient():
    OPENFDA_API_URL="api.fda.gov"
    OPENFDA_API_EVENT= "/drug/event.json"

    def get_events(self, item, search, search_drug, limit):
        url = ''
        if search == True:
            if search_drug == True:
                search_type="?search=patient.drug.medicinalproduct:"
            else:
                search_type="?search=companynumb:"

            url = self.OPENFDA_API_EVENT + search_type + item + "&limit=" + limit

        else:
            url = self.OPENFDA_API_EVENT + "?limit=" + limit

        conn=http.client.HTTPSConnection(self.OPENFDA_API_URL)
        conn.request("GET", url)
        r1=conn.getresponse()
        data1=r1.read()
        data=data1.decode("utf8")
        events=data
        return events

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def check_limit(self, limit):
        try:
            int(limit)
            return True
        except ValueError:
            return False

    def get_correct_answer(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

    def do_GET(self):
        client=OpenFDAClient()
        html=OpenFDAHTML()
        parser=OpenFDAParser()
        main_html= html.get_main_page()

        limit_ok = True

        if 'list' in self.path and 'search' not in self.path:
            limit=self.path.split("=")[1]
            limit_ok =self.check_limit(limit)

        if limit_ok == False:
            self.send_response(400)
            self.send_header('Content-type','text/html')
            self.end_headers()
            html=html.get_page_not_correct_limit()
            self.wfile.write(bytes(html, "utf8"))

        else:
            if self.path =='/':
                self.get_correct_answer()
                self.wfile.write(bytes(main_html, "utf8"))

            elif "/listDrugs" in self.path:
                self.get_correct_answer()
                events= client.get_events(None, False, None, limit)
                events= json.loads(events)
                events=events["results"]
                drugs=parser.get_drugs_from_events(events)
                list_html=html.get_list_html(drugs)
                self.wfile.write(bytes(list_html, "utf8"))

            elif "/listCompanies" in self.path:
                self.get_correct_answer()
                events=client.get_events(None, False, None, limit)
                events= json.loads(events)
                events=events["results"]
                companies=parser.get_companies_from_events(events)
                list_html=html.get_list_html(companies)
                self.wfile.write(bytes(list_html,"utf8"))

            elif "/searchDrug" in self.path:
                self.get_correct_answer()
                drug=self.path.split("=")[1]
                events=client.get_events(drug,True, True, '10')
                events= json.loads(events)
                events=events["results"]
                companies=parser.get_companies_from_events(events)
                list_html=html.get_list_html(companies)
                self.wfile.write(bytes(list_html,"utf8"))

            elif "/searchCompany" in self.path:
                self.get_correct_answer()
                company_numb=self.path.split("=")[1]
                events=client.get_events(company_numb, True, False, '10')
                events=json.loads(events)
                events=events["results"]
                drugs=parser.get_drugs_from_events(events)
                list_html=html.get_list_html(drugs)
                self.wfile.write(bytes(list_html,"utf8"))

            elif "/listGender" in self.path:
                self.get_correct_answer()
                events=client.get_events(None, False, None, limit)
                events= json.loads(events)
                events=events["results"]
                numbers_patients_sex=parser.get_genders_from_events(events)
                list_html=html.get_list_html(numbers_patients_sex)
                self.wfile.write(bytes(list_html, "utf8"))

            elif "/redirect" in self.path or "/back" in self.path:
                self.send_response(302)
                self.send_header('Location','http://localhost:8000/')
                self.end_headers()

            elif "/secret" in self.path:
                self.send_response(401)
                self.send_header('WWW-Authenticate','Basic realm="\"Test"')
                self.end_headers()

            else:
                self.send_response(404)
                self.send_header('Content-type','text/html')
                self.end_headers()
                html=html.get_page_not_found()
                self.wfile.write(bytes(html, "utf8"))

        return
