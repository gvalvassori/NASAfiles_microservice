from os.path import join
from bs4 import BeautifulSoup
from fastapi import HTTPException
import requests
from datetime import datetime, timedelta, timezone
import logging


__copyright__ = 'Copyright (c) 2021 Ascentio Technologies S.A.'


class SessionWithHeaderRedirection(requests.Session):

    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != 'urs.earthdata.nasa.gov' and original_parsed.hostname != 'urs.earthdata.nasa.gov':
                del headers['Authorization']
        return

class Download(object):
    def __init__(self, log, user, password):
        self._logger = log
        self.urs_file = None
        self.urs_username = user
        self.urs_password = password

    def _logging_oceandata(self):
        '''
        Logging with ocean data server
        '''
        self._logger.info('Logging with ocean data server')
        self._logger.debug('user name : %s', self.urs_username)
        self._logger.debug('password : %s', self.urs_password)
        return SessionWithHeaderRedirection(self.urs_username, self.urs_password)

    def download(self, base_url, filter_list, filter_date='@today'):
        """
        Download files list from ocean data server

        :param base_url: Url including the mission and product's level of the
            products to download, but no the year and julian day. Example:
            https://oceandata.sci.gsfc.nasa.gov/Ancillary/Meteorological
        :type base_url: Str
        :param filter_list: List of files
        :type filter_list: List of Str
        :param filter_date: Date of the products to download.
        :type filter_date: Str
        :return:
        """
        self._logger.info('Starting to download product list')
        self._logger.info('- Base url: {}'.format(base_url))
        self._logger.info('- Filter products: {}'.format(filter_list))
        self._logger.info('- Filter date: {}'.format(filter_date))

        download_date = self._validate_date(filter_date)
        product_list_url = self._build_url(base_url, *download_date)

        if filter_list:
            url_list = self._get_file_list(url=product_list_url)
            file_list = self._generate_file_list(filter_list, url_list)
            amount_download_all_file = len(file_list)
            self._logger.info('Filter completed. With {} items to download'.format(amount_download_all_file))
            if amount_download_all_file!=0:
                self._download_file_list(file_list)
                # TODO: implementar guardado en cloud storage / s3
                # TODO: si viene un parametro que sea local entonces guardarlo localmente
            else:
                self._logger.info('Not files to download')
                raise HTTPException(status_code=404, detail='Not files to download')
        else:
            self._logger.info('Not files to download')
            raise HTTPException(status_code=404, detail='Not files to download')

    def _download_file_list(self, file_list):
        """
        Download file list.
        """
        amount_download_all_file = len(file_list)
        count_download_file = 0
        try:
            session = self._logging_oceandata()
            for file in file_list:
                url = join('https://oceandata.sci.gsfc.nasa.gov/ob/getfile/', file)
                file_name = join("./", file) 
                self._download_file(session, url, file_name)
                count_download_file += 1
            session.close()
        except Exception as e:
            self._logger.info('{} of {} files were downloaded'.format(count_download_file, amount_download_all_file))
            session.close()
            raise e
        self._logger.info('{} of {} files were downloaded'.format(count_download_file, amount_download_all_file))



    def _download_file(self, session, url, filename, retries=11):
        """
        Download file
        """
        try:
            self._logger.info('Starting file download %s', filename)
            for retries_amoun in range(1, retries):
                response = session.get(url, stream=True, allow_redirects=True)
                if response.status_code == 200:
                    break
                self._logger.info('Download retries number %i', retries_amoun)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self._logger.error('Reponse Error : %s', str(e))
        try:
            with open(filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    fd.write(chunk)
            self._logger.info('Finish file download %s', filename)
        except EnvironmentError as err:
            err_msg = err
            self._logger.error('File write error: {}'.format(err_msg))

    def _generate_file_list(self, filter_list, file_list):
        """
        Generate list of files from filter list
        :param filter_list:
        :param file_list:
        :return:
        """
        final_list = []
        for fil in filter_list:
            f_name, r_equal = self._validate_name(fil)
            if r_equal:
                temp_list = [f_name] if f_name in file_list and f_name not in final_list else []
            else:
                temp_list = [f for f in file_list if f_name in f and f not in final_list]
            final_list = final_list + temp_list
        return final_list

    def _validate_name(self, file_name):
        """
        Validate file names
        *nc* *nc nc* *
        :param file_name:
        :return:
        """
        if file_name.count('*') < 3:
            f_name = file_name
            r_equal = True
            if f_name.startswith('*'):
                f_name = f_name[1:]
                r_equal = False
            if f_name.endswith('*'):
                f_name = f_name[:-1]
                r_equal = False
            if '*' in f_name:
                err_msg = 'Incorrect name. Incorrect position of *: {}'.format(file_name)
                self._logger.error(err_msg)
            return f_name, r_equal
        else:
            err_msg = 'Incorrect name. Has more an *: {}'.format(file_name)
            self._logger.error(err_msg)

    def _validate_date(self, filter_date):
        """
        Validate date to download. If filter_date is None, return the current
        date
        :param filter_date: Date to parse
        :type filter_date: Str
        :return: parsed date (year and julian day)
        :type return: tuple (year<String>, julian day<String>)
        """
        now = datetime.now(timezone.utc)
        if filter_date == '@today':
            _filter_date = now
            self._logger.info('Date @today set to {}'.format(_filter_date))
        elif filter_date == '@yesterday':
            _filter_date = now - timedelta(days=1)
            self._logger.info('Date @yesterday set to {}'.format(_filter_date))
        else:
            self._logger.debug('Parsing date {}'.format(filter_date))
            try:
                _filter_date = datetime.strptime(filter_date, '%Y%m%d')
                if _filter_date > now:
                    pass
            except:
                pass

        _filter_date_y = _filter_date.year
        _filter_date_j = _filter_date.timetuple().tm_yday
        return (_filter_date_y, _filter_date_j)

    @staticmethod
    def _build_url(base_url, year, jday):
        '''
        Builds the url taking a base url and adding the given year and julian
        day

        :param base_url (str): the base url
        :param year (int): the year part of the date to get the products
        :param jday (int): the julian day part of the date to get the products
        :return (str): the url to download the product list
        '''
        _base_url = base_url[:-1] if base_url.endswith('/') else base_url
        _year = str(year)
        _jday = str(jday).rjust(3, '0')
        return '{}/{}/{}'.format(_base_url, _year, _jday)

    def _get_file_list(self, url, retries=10):
        """
        Get list of files from OCEAN DATA
        Now get from url config, but we need implemenent the parse from date.
        TODO: When implement the feature of DATE, only need pass the correct url
        :param url (str): url of product list
        :param retries (int): Num of retries
        :return:
        """
        self._logger.info('Starting download file list from {}'.format(url))
        try:
            session = self._logging_oceandata()
            for retries_amount in range(0, retries):
                response = session.get(url, stream=True, allow_redirects=True)
                if response.status_code == 200:
                    break
                self._logger.info('Download list retries number %i', retries_amount)
            session.close()
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            err_msg = 'Reponse Error : {}'.format(err)
            self._logger.error(err_msg)

        self._logger.info('Starting parse data from request')
        soup = BeautifulSoup(response.text, features="html.parser")
        table = soup.find('table')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        if not rows:
            err_msg = 'Empty table. Check the url'
            self._logger.error(err_msg)
        file_list = [row.find('td').text.strip() for row in rows if row]
        self._logger.info('Parse completed. Returning list with {} items'.format(len(file_list)))
        return file_list

logger = logging.getLogger(__name__)

file_output = Download(logger, "gcrisnejo", "gcrisnejoA98")
file_output.download(
                "https://oceandata.sci.gsfc.nasa.gov/directdataaccess/Ancillary/GLOBAL",
                ["GMAO_MERRA2.20230628T100000.MET.nc"],
                "20230628",
            )