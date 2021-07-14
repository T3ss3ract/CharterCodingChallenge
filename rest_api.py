import json
import csv
import pprint

from flask import Flask, send_from_directory

ppr = pprint.PrettyPrinter(indent=2, sort_dicts=False)

UPLOAD_DIRECTORY = "./"  # files will be stored in the same directory the program runs in, for the sake of simplicity

api = Flask(__name__)  # make a flask app on this program

# ------------------------------------------------------------- HELPER FUNCTIONS
with open("db.json", "r") as dbfile:
    db = json.load(dbfile)
    # this loads the data from db.json into memory so we can access/manipulate it during program runtime.


def prep_csv_file_for_download(key):
    """
    This will take the parsed data from the extracted json and will allow us to sort them based
    on the key passed to the function. this is called on the download api endpoint to create the proper csv file before
    sending it to the user.

    :param key: the key to sort by, either orgname, relcount, or labor
    :return: nothing, will make a file with the correctly ordered csv values
    """
    data_ = open("sorted_file.csv", "w")
    csvw = csv.writer(data_)
    count = 0
    lines = sort_by_key(key)
    for orgdata in lines:
        if count == 0:
            header = orgdata.keys()
            csvw.writerow(header)
            count += 1
        csvw.writerow(orgdata.values())
    data_.close()
    return


def collect_organization_info(organization):
    """
    Will parse all of the needed info from the data returned at the web endpoint given to us,organization, release
    count, total labor hours, all in production, licenses, and most active month.

    :param organization: the organization we are looking to parse information on
    :return: organization, release
    count, total labor hours, all in production, licenses, and most active month.
    """
    datearray = [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ]  # need 13 zeros for date calculation
    release_count = 0
    total_labor_hours = 0
    all_in_production = True
    licenses = []
    for item in db["releases"]:
        if item["organization"] == organization:
            date_string = item["date"]["created"]
            date_string = date_string.split("-")
            month = int(date_string[1])
            datearray[month] = datearray[month] + 1
            total_labor_hours += item["laborHours"]
            release_count = release_count + 1
            if item["status"] != "Production":
                all_in_production = False
            try:
                licenses.append(item["permissions"]["licenses"][0]["name"])
            except:  # we may not have a license in the release. if there is an exception raised when trying to add this
                pass  # field, we move to the next one
    print(total_labor_hours)
    print(release_count)
    print(all_in_production)
    print(licenses)
    print(datearray)
    active_month = datearray.index(max(datearray))
    print()
    return (
        organization,
        release_count,
        total_labor_hours,
        all_in_production,
        licenses,
        [active_month],
    )


def read_org_from_json(organization):
    """
    makes the json response for a single organization. Will be used in other functions to build a working list
    containing all the organizations.

    :param organization: exact name of organization (will be parsed for us in a helper function)
    :return: a json body with a single blob with organization data
    """
    (
        org,
        rel_ct,
        total_labor,
        all_in_prod,
        licenses,
        active_month,
    ) = collect_organization_info(organization)
    response = {
        "organization": org,
        "release_count": rel_ct,
        "total_labor_hours": total_labor,
        "all_in_production": all_in_prod,
        "licenses": licenses,
        "most_active_months": active_month,
    }
    ppr.pprint(response)
    return response


def get_org_list():
    """
    parses all of the organization names from the large json blob (see it in db.json) and adds them to a list for
    parsing. This iwll make the list of all organizations in the blob.

    :return: list of all organizations within the blob.
    """
    org_list = []
    for item in db["releases"]:
        if item["organization"] not in org_list:
            org_list.append(item["organization"])
    return org_list


def sort_by_key(key):
    """
    used in both endpoints to sort the parsed data by the provided key.

    key: the key to sort by, either orgname, relcount, or labor
    :param key:
    :return:
    """
    if key == "orgname":
        lines = sorted(org_master_list, key=lambda k: k["organization"])
    elif key == "relcount":
        lines = sorted(org_master_list, key=lambda k: k["release_count"])
    elif key == "labor":
        lines = sorted(org_master_list, key=lambda k: k["total_labor_hours"])
    else:
        return []
    return lines


@api.route("/json/<id>")
def serve_response_from_api(id):
    """
    API endpoint for receiving json data from the API. in order to query,
    go to the url 127.0.0.1:3751/json/<orgname/relcount/labor> to view the results
    in json format.

    note that the results are in ascending order.

    :param id: id is one of [orgname, relcount, labor]
    :return: a web response containing the json payload information
    """
    response = sort_by_key(id)
    org_response = {"organizations": response}
    resp = json.dumps(org_response, indent=4)
    print(resp)
    return resp


@api.route("/csv/<id>")
def download_csv(id):
    """
    API endpoint for receiving a .csv file download. In order to query,
    go to the url 127.0.0.1:3751/json/<orgname/relcount/labor> to receive a file download
    with the items ordered in the proper way.

    A note is that this will create a static (yet overwriteable) file containing the results in the correct order,
    called sorted_file.csv. this file will be changed when a different csv endpoint is hit and change the file with the
    new results when the endpoint is queried. Flask has a very flexible download system that can mesh well with
    existing architecture to serve files from multiple directories. In this case, the serving directory is the directory
    containing `rest_api.py`

    note that the results are in ascending order.

    :param id: one of <orgname/relcount/labor>
    :return:
    """
    prep_csv_file_for_download(id)
    return send_from_directory(UPLOAD_DIRECTORY, "sorted_file.csv", as_attachment=True)


# ------------------------------------------------------------- MAIN
if __name__ == "__main__":
    org_list = get_org_list()  # build org list at runtime
    global org_master_list  # globally defined variable will be used in  parsing functions
    org_master_list = []
    for item in org_list:
        org_blob = read_org_from_json(item)
        org_master_list.append(org_blob)
    # for item in db["releases"]:
    # print(item["organization"])
    test_string = "Office of Scientific and Technical Information (OSTI)"
    test_string_2 = "Sandia National Laboratories (SNL)"
    print("starting web api. use the REST API to search by organization name.")
    print("================")
    # read_org_from_json(test_string)
    print("SERVING NOW")
    api.run(debug=True, port=3751)
