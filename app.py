import pandas as pd
from owlready2 import *
from SPARQLWrapper import SPARQLWrapper, JSON
import csv

# Step 1: SPARQL Query to Wikidata and save to CSV
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

query = """
SELECT DISTINCT ?AppLabel ?DeveloperLabel ?OSLabel ?LanguageLabel ?LicenseLabel ?CopyrightStatusLabel
WHERE {
   wd:Q7397 ^wdt:P279* / ^wdt:P31 ?App .
   ?App wdt:P178 ?Developer.
   ?App wdt:P306 ?OS.
   ?App wdt:P275 ?License.
   ?App wdt:P6216 ?CopyrightStatus.
   ?App wdt:P277 ?Language.
   SERVICE wikibase:label {
     bd:serviceParam wikibase:language "en" .
   }
}
"""

sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

# Step 2: Save SPARQL results to CSV
csv_filename = "Apps.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["App", "Developer", "OperatingSystem", "Language", "License", "CopyrightStatus"])  # Header

    for result in results["results"]["bindings"]:
        writer.writerow([
            result["AppLabel"]["value"],
            result["DeveloperLabel"]["value"],
            result["OSLabel"]["value"],
            result["LanguageLabel"]["value"],
            result["LicenseLabel"]["value"],
            result["CopyrightStatusLabel"]["value"]
        ])

print(f"SPARQL results saved to {csv_filename}")

# Step 3: Load the CSV Data
data = pd.read_csv(csv_filename)
print("CSV columns:", data.columns)

# Step 4: Create Ontology
onto = get_ontology("http://test.org/apps.owl")

with onto:
    class Apps(Thing): pass
    class Developer(Thing): pass
    class OperatingSystem(Thing): pass
    class Language(Thing): pass
    class License(Thing): pass
    class CopyrightStatus(Thing): pass

    class is_developed_by(ObjectProperty, FunctionalProperty):
        domain = [Apps]
        range = [Developer]
    class works_on(ObjectProperty, FunctionalProperty):
        domain = [Apps]
        range = [OperatingSystem]
    class is_written_in(ObjectProperty, FunctionalProperty):
        domain = [Apps]
        range = [Language]
    class has_license(ObjectProperty, FunctionalProperty):
        domain = [Apps]
        range = [License]
    class has_copyright_status(ObjectProperty, FunctionalProperty):
        domain = [Apps]
        range = [CopyrightStatus]

# Step 5: Populate Ontology with CSV Data
with onto:
    for _, row in data.iterrows():
        app_ind = onto.Apps(row[0])
        dev_ind = onto.Developer(row[1])
        os_ind = onto.OperatingSystem(row[2])
        lang_ind = onto.Language(row[3])
        license_ind = onto.License(row[4])
        copyright_status_ind = onto.CopyrightStatus(row[5])
        
        app_ind.is_developed_by = dev_ind
        app_ind.works_on = os_ind
        app_ind.is_written_in = lang_ind
        app_ind.has_license = license_ind
        app_ind.has_copyright_status = copyright_status_ind

# Step 6: Save the Ontology
onto.save("App.owl")
print("Ontology saved to App.owl")
