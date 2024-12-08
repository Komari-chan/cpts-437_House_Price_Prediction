import requests
import regex as re
import csv
import concurrent.futures

def download_html(url):
    try:
        click_accept = True
        while click_accept == True:
            with open('cookieKey.txt', 'r') as file:
                cookie_key = file.read().strip()
            session = requests.Session()
            cookies = {
                'FormsAuthentication': cookie_key,
            }
            response = session.get(url, cookies=cookies)
            response.raise_for_status()  # Check if the request was successful

            if response.text.find("Disclaimer and Terms of Service") == -1:
                click_accept = False
                return response.text
            else:
                print(url)
                print("Please update cookieKey.txt with the correct cookie key and press enter to continue.")
                input()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the HTML content: {e}")
        return None

def download_both_pages(url):
    response_assessor = download_html(url)
    url = url.replace("Assessor", "AppraisalDetails")
    response_appraisal = download_html(url)
    return (response_assessor, response_appraisal)

def extract_appraisal_details(details = None):
    if details:
        content = details
    else:
        with open("AppraisalDetails.html", 'r', encoding='utf-8') as file:
            content = file.read()

    # define vars
    address = None
    town = None
    dor_code = None
    total_area = None
    year_built = None
    remodel_year = None
    quality = None
    condition = None
    architecture = None
    bedrooms = None
    bathrooms = None
    total_rooms = None
    foundation = None
    garage_stalls = None

    try:
        # Extract the address
        address_match = re.search(r'<span id="cphContent_ParcelOwnerInfo1_lbAddress">(.*?)</span>', content, timeout=3, concurrent=True)
        address = address_match.group(1) if address_match else None

        # Extract the town
        town_math = re.search(r'<span id="cphContent_ParcelOwnerInfo1_lbCity">(.*?)</span>', content, timeout=3, concurrent=True)
        town = town_math.group(1) if town_math else None

        # extract DOR code
        dor_code_match = re.search(r'<span id="cphContent_ParcelOwnerInfo1_lbMID1Value">(.*?)</span>', content, timeout=3, concurrent=True)
        dor_code = dor_code_match.group(1) if dor_code_match else None

        # Extract the table values
        table_match = re.search(
            r'<table.*?class="dataGrid".*?>.*?<tr>.*?<th>.*?Total Area.*?</th>.*?<th>.*?Year Built.*?</th>.*?<th>.*?Remodel Year.*?</th>.*?<th>.*?Quality.*?</th>.*?<th>.*?Condition.*?</th>.*?</tr>.*?<tr>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?</tr>.*?</table>',
            content, re.DOTALL, timeout=3, concurrent=True
        )
        
        if table_match:
            total_area = table_match.group(1).strip()
            year_built = table_match.group(2).strip()
            remodel_year = table_match.group(3).strip()
            quality = table_match.group(4).strip()
            condition = table_match.group(5).strip()
        else:
            total_area = None
            year_built = None
            remodel_year = None
            quality = None
            condition = None

        # Extract additional table values
        building_data_match = re.search(
            r'<table.*?id="grdBuildingData".*?>.*?<tr>.*?<td>Architecture</td>.*?<td>(.*?)</td>.*?</tr>.*?<tr.*?>.*?<td>Bedrooms</td>.*?<td>(.*?)</td>.*?</tr>.*?<tr>.*?<td>Bathrooms</td>.*?<td>(.*?)</td>.*?</tr>.*?<tr.*?>.*?<td>Total Rooms</td>.*?<td>(.*?)</td>.*?</tr>.*?<tr>.*?<td>Foundation</td>.*?<td>(.*?)</td>.*?</tr>.*?<tr.*?>.*?<td>Garage Stalls</td>.*?<td>(.*?)</td>.*?</tr>.*?</table>',
            content, re.DOTALL, timeout=3, concurrent=True
        )

        if building_data_match:
            architecture = building_data_match.group(1).strip()
            bedrooms = building_data_match.group(2).strip()
            bathrooms = building_data_match.group(3).strip()
            total_rooms = building_data_match.group(4).strip()
            foundation = building_data_match.group(5).strip()
            garage_stalls = building_data_match.group(6).strip()

            bedrooms = re.sub(r'[^\d.]', '', bedrooms)
            bathrooms = re.sub(r'[^\d.]', '', bathrooms)
            total_rooms = re.sub(r'[^\d.]', '', total_rooms)
            garage_stalls = re.sub(r'[^\d.]', '', garage_stalls)
        else:
            architecture = None
            bedrooms = None
            bathrooms = None
            total_rooms = None
            foundation = None
            garage_stalls = None
    
    except Exception as e:
        print(f"Error extracting the appraisal details: {e}")

    return {
        'Address': address,
        'Town': town,
        'DOR_Code': dor_code,
        'Total_Area': total_area,
        'Year_Built': year_built,
        'Remodel_Year': remodel_year,
        'Quality': quality,
        'Condition': condition,
        'Architecture': architecture,
        'Bedrooms': bedrooms,
        'Bathrooms': bathrooms,
        'Total_Rooms': total_rooms,
        'Foundation': foundation,
        'Garage_Stalls': garage_stalls
    }

def extract_assessor_details(details = None):
    if details:
        content = details
    else:
        with open("Assessor.html", 'r', encoding='utf-8') as file:
            content = file.read()
    
    # define vars
    land_value = None
    improvements_value = None
    permanent_crop_value = None
    total_value = None
    total_acres = None

    try:
        # Extract market values
        market_values_match = re.search(
            r'<table.*?id="cphContent_ctl00_dvMarketValues".*?>.*?<tr>.*?<td>Land:</td><td align="right">(.*?)</td>.*?</tr>.*?<tr.*?>.*?<td>Improvements:</td><td align="right">(.*?)</td>.*?</tr>.*?<tr>.*?<td>Permanent Crop:</td><td align="right">(.*?)</td>.*?</tr>.*?<tr.*?>.*?<td>.*?Total.*?</td><td align="right">(.*?)</td>.*?</tr>.*?</table>',
            content, re.DOTALL, timeout=3, concurrent=True
        )

        if market_values_match:
            land_value = market_values_match.group(1).strip()
            improvements_value = market_values_match.group(2).strip()
            permanent_crop_value = market_values_match.group(3).strip()
            total_value = market_values_match.group(4).strip()

            land_value = re.sub(r'[^\d.]', '', land_value)
            improvements_value = re.sub(r'[^\d.]', '', improvements_value)
            permanent_crop_value = re.sub(r'[^\d.]', '', permanent_crop_value)
            total_value = re.sub(r'[^\d.]', '', total_value)
        else:
            land_value = None
            improvements_value = None
            permanent_crop_value = None
            total_value = None

        # Extract total acres
        total_acres_match = re.search(
            r'<table.*?id="cphContent_ctl00_dvAssessmentData".*?>.*?<tr.*?>.*?<td>Total Acres:</td>.*?<td.*?>(.*?)</td>.*?</tr>.*?</table>',
            content, re.DOTALL, timeout=3, concurrent=True
        )

        if total_acres_match:
            total_acres = total_acres_match.group(1).strip()
        else:
            total_acres = None

    except Exception as e:
        print(f"Error extracting the assessor details: {e}")

    return {
        'Land_Value': land_value,
        'Improvements_Value': improvements_value,
        'Permanent_Crop_Value': permanent_crop_value,
        'Total_Value': total_value,
        'Total_Acres': total_acres
    }

def from_url_get_all_details(url):
    assessor, appraisal = download_both_pages(url)
    assessor_details = extract_assessor_details(assessor)
    appraisal_details = extract_appraisal_details(appraisal)

    combined_details = {**appraisal_details, **assessor_details}
    return combined_details

def from_parcels_make_csv_of_details(parcels_filename):
    with open(parcels_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        parcels = [row for row in reader]

    def process_parcel(parcel):
        url = parcel['DATA_LINK']
        details = from_url_get_all_details(url)
        return details

    with open("details.csv", "w") as file:
        file.write("Address,Town,DOR_Code,Total_Area,Year_Built,Remodel_Year,Quality,Condition,Architecture,Bedrooms,Bathrooms,Total_Rooms,Foundation,Garage_Stalls,Land_Value,Improvements_Value,Permanent_Crop_Value,Total_Value,Total_Acres,Data_Link\n")
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_parcel = {executor.submit(process_parcel, parcel): parcel for parcel in parcels}
            for future in concurrent.futures.as_completed(future_to_parcel):
                parcel = future_to_parcel[future]
                try:
                    details = future.result()
                    print(details)
                    file.write(f"{details['Address']},{details['Town']},{details['DOR_Code']},{details['Total_Area']},{details['Year_Built']},{details['Remodel_Year']},{details['Quality']},{details['Condition']},{details['Architecture']},{details['Bedrooms']},{details['Bathrooms']},{details['Total_Rooms']},{details['Foundation']},{details['Garage_Stalls']},{details['Land_Value']},{details['Improvements_Value']},{details['Permanent_Crop_Value']},{details['Total_Value']},{details['Total_Acres']},{parcel['DATA_LINK']}\n")
                except Exception as e:
                    print(f"Error processing parcel {parcel['DATA_LINK']}: {e}")

if __name__ == "__main__":
    url = "http://terrascan.whitmancounty.net/Taxsifter/Assessor.aspx?keyId=935211&parcelNumber=200004512232540&typeID=1"
    # download_both_pages(url)
    # print(from_url_get_all_details(url))

    from_parcels_make_csv_of_details("Whitman_parcels_with_buildings.csv")