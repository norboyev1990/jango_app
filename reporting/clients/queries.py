class Query():

    @staticmethod
    def findClients():
        return '''
            SELECT 
                UNIQUE_CODE AS ClientID,
                MAX(NAME_CLIENT) AS ClientName,
                MAX(SUBJECT) AS ClientType,
                SUM(VSEGO_ZADOLJENNOST) AS TotalLoans,
                MAX(ADRESS_CLIENT) AS Address
            from credits
            WHERE REPORT_id = %s AND CLIENT_TYPE = 'J'
            GROUP BY UNIQUE_CODE
            
        '''

    @staticmethod
    def findClientByID():
        return '''
            SELECT ClientID,
                MAX(ClientName),
                MAX(ClientType),
                COUNT(*) AS CountLoans, 
                SUM(VSEGO_ZADOLJENNOST)  AS TotalLoans,
                MAX(substr(ADRESS_CLIENT, 1, pos-1)) AS Address,
                MAX(substr(ADRESS_CLIENT, pos+1)) AS Phone
            FROM (
                SELECT 
                    UNIQUE_CODE AS ClientID,
                    NAME_CLIENT AS ClientName,
                    CASE SUBJECT 
                        WHEN TRANSLATE('ЮЛ' USING nchar_cs) THEN 'ЮРИДИЧЕСКОЕ ЛИЦА'
                        WHEN TRANSLATE('ИП' USING nchar_cs) THEN 'ИНДИВИДУАЛНОЕ ПРЕДПРИЯТИЯ'
                        ELSE 'ФИЗИЧЕСКОЕ ЛИЦА' END AS ClientType,
                    VSEGO_ZADOLJENNOST ,
                    CASE instr(ADRESS_CLIENT,',') WHEN 0 THEN 999 ELSE instr(ADRESS_CLIENT,',') END  AS POS,
                    ADRESS_CLIENT
                from credits
                WHERE REPORT_id=4
                ) T
            WHERE ClientID LIKE '04926110'
            GROUP BY ClientID
        '''