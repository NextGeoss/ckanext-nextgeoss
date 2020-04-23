"""Tests for helpers.py."""

from ckanext.nextgeoss import helpers
import mock
import requests

class TestHelpers(object):

    @mock.patch('ckanext.nextgeoss.helpers.requests.get')
    def test_get_linker_service_resources_found(self, mock_get):   
        dataset_name = "s1a_iw_slc__1sdv_20200422t150816_20200422t150844_032242_03bac7_6dba"
        source_link = "https://sentinels.space.noa.gr/dhus/odata/v1/Products('aba3a5f3-d6cc-497c-a0ce-0d1732d6aa16')/$value"
        response = {
            "feed": {
                "entry": [
                    {
                        "title": "s1a_iw_slc__1sdv_20200422t150816_20200422t150844_032242_03bac7_6dba",
                        "id": "aba3a5f3-d6cc-497c-a0ce-0d1732d6aa16",
                        "summary": "Date: 2020-04-23T05:35:46.921Z, Instrument: SAR-C SAR, Mode: VV VH, Satellite: Sentinel-1, Size: 1.6 GB",
                        "sources": {
                            "link": {
                                "href": source_link,
                            }
                        }
                    }
                ]
            }
        }
        
        mock_get().configure_mock(status_code=200)
        mock_get().json.return_value = response
        assert(helpers.get_linker_service_resources(dataset_name, testing=True) == [source_link])

    @mock.patch('ckanext.nextgeoss.helpers.requests.get')
    def test_get_linker_service_resources_not_found(self, mock_get):   
        dataset_name = "s1a_iw_slc__1sdv_20200422t150816_20200422t150844_032242_03bac7_6dba"
        response = {
            "feed": {}
        }
       
        mock_get().configure_mock(status_code=200)
        mock_get().json.return_value = response
        assert(helpers.get_linker_service_resources(dataset_name, testing=True) == [])

    @mock.patch('ckanext.nextgeoss.helpers.requests.get')
    def test_get_linker_service_resources_timeout(self, mock_get):   
        dataset_name = "s1a_iw_slc__1sdv_20200422t150816_20200422t150844_032242_03bac7_6dba"
        mock_get().side_effect = requests.exceptions.ReadTimeout()
        assert(helpers.get_linker_service_resources(dataset_name, testing=True) == [])
    
    @mock.patch('ckanext.nextgeoss.helpers.requests.get')
    def test_get_linker_service_resources_http_error(self, mock_get):   
        dataset_name = "s1a_iw_slc__1sdv_20200422t150816_20200422t150844_032242_03bac7_6dba"
        mock_get().side_effect = requests.exceptions.HTTPError()
        assert(helpers.get_linker_service_resources(dataset_name, testing=True) == [])