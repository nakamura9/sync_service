import pyodbc
from loggers import logger
import time
import requests
import json
import datetime
import os 


# For dev



logger.info("running service")

WORKING_DIR = "C:\goprime\sync_service"
config = None 
with open (os.path.join(WORKING_DIR, "config.json"), "r") as f:
    config = json.load(f)

HEADERS = {
    "Authorization": config.get('token'),
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def to_dict(row):
    return dict(zip([t[0] for t in row.cursor_description], row))

def get_sales_orders(conn, frm=None, as_json=True):
    '''Get all the sales orders from the database'''
    cursor = conn.cursor()
    logger.info("Successfully connected.")
    filters = """
        WHERE fQuantity > fQtyProcessed 
        AND DocumentStateDesc not in ( 'Archived', 'Quote', 'Cancelled', 'Template')
        AND (QtyOutstanding / fQuantity) > 0.1    
    """
    if frm:
        if isinstance(frm, str):
            frm = datetime.datetime.strptime(frm, "%Y-%m-%d %H:%M:%S")
        filters += " AND OrderDate > '{}'".format(frm.strftime("%Y-%m-%d %H:%M:%S"))

    cursor.execute("""
        SELECT [OrderNum]
            ,[ExtOrderNum]
            ,[OrderDate]
            ,[Code]
            ,[QtyOutstanding] as fQuantity
            ,[Account]
            ,[Name]
            ,[Description_1]
            ,[fUnitPriceIncl]
            ,[fUnitPriceExcl]
            ,[dTimeStamp]
        FROM [Alpha Packaging].[dbo].[_bvSalesOrdersFull]
        {}
    """.format(filters))

    values = [to_dict(r) for r in cursor]

    if as_json:
        return json.dumps(values, default=str)
    return values

def main():
    '''
    use pyodbc.drivers() to get the driver list.
    Get server name from the properties of the database server.
    validate database name
    '''
    logger.info("Connecting to database")
    conn = pyodbc.connect(
        "Driver=ODBC Driver 11 for SQL Server;"
        f"Server={config.get('server')};"
        f"Database={config.get('database')};"
        f"user={config.get('user')};"
        f"password={config.get('password')};"
        "Trusted_Connection=yes;"
    )

    resp = requests.get(
        f"http://{config.get('host')}/api/method/"
        "alpha_packaging.alpha_packaging.public_api.last_order", 
        headers=HEADERS
    )
    logger.info(resp.content)
    latest = resp.json().get("message", {}).get("latest")
    if latest:
        # only get latest items
        logger.info(f"Collecting data since {latest}")
        data = get_sales_orders(conn, latest)
    else:
        # initial fetch of data 
        logger.info("Collecting all orders")
        data = get_sales_orders(conn)

    resp = requests.get(
        f"http://{config.get('host')}/api/method/"
        "alpha_packaging.alpha_packaging.public_api.sync_orderbook", 
        headers=HEADERS, 
        json={"orders": data}
    )
    if resp.status_code == 200:
        logger.info("Successfully synced orderbook")
    else:
        logger.error("Failed to sync order book.")

    # if latest:
        # insert update sales order book here.
        # pass
    logger.info(resp.content)


if __name__ == "__main__":
    main()


"""
    SELECT [idInvoiceLines]
      ,[iInvoiceID]
      ,[iOrigLineID]
      ,[iGrvLineID]
      ,[iLineDocketMode]
      ,[cDescription]
      ,[iUnitsOfMeasureStockingID]
      ,[iUnitsOfMeasureCategoryID]
      ,[iUnitsOfMeasureID]
      ,[fQuantity]
      ,[fQtyChange]
      ,[fQtyToProcess]
      ,[fQtyLastProcess]
      ,[fQtyProcessed]
      ,[fQtyReserved]
      ,[fQtyReservedChange]
      ,[cLineNotes]
      ,[fUnitPriceExcl]
      ,[fUnitPriceIncl]
      ,[iUnitPriceOverrideReasonID]
      ,[fUnitCost]
      ,[fLineDiscount]
      ,[iLineDiscountReasonID]
      ,[iReturnReasonID]
      ,[fTaxRate]
      ,[bIsSerialItem]
      ,[bIsWhseItem]
      ,[fAddCost]
      ,[cTradeinItem]
      ,[iStockCodeID]
      ,[iJobID]
      ,[iWarehouseID]
      ,[iTaxTypeID]
      ,[iPriceListNameID]
      ,[fQuantityLineTotIncl]
      ,[fQuantityLineTotExcl]
      ,[fQuantityLineTotInclNoDisc]
      ,[fQuantityLineTotExclNoDisc]
      ,[fQuantityLineTaxAmount]
      ,[fQuantityLineTaxAmountNoDisc]
      ,[fQtyChangeLineTotIncl]
      ,[fQtyChangeLineTotExcl]
      ,[fQtyChangeLineTotInclNoDisc]
      ,[fQtyChangeLineTotExclNoDisc]
      ,[fQtyChangeLineTaxAmount]
      ,[fQtyChangeLineTaxAmountNoDisc]
      ,[fQtyToProcessLineTotIncl]
      ,[fQtyToProcessLineTotExcl]
      ,[fQtyToProcessLineTotInclNoDisc]
      ,[fQtyToProcessLineTotExclNoDisc]
      ,[fQtyToProcessLineTaxAmount]
      ,[fQtyToProcessLineTaxAmountNoDisc]
      ,[fQtyLastProcessLineTotIncl]
      ,[fQtyLastProcessLineTotExcl]
      ,[fQtyLastProcessLineTotInclNoDisc]
      ,[fQtyLastProcessLineTotExclNoDisc]
      ,[fQtyLastProcessLineTaxAmount]
      ,[fQtyLastProcessLineTaxAmountNoDisc]
      ,[fQtyProcessedLineTotIncl]
      ,[fQtyProcessedLineTotExcl]
      ,[fQtyProcessedLineTotInclNoDisc]
      ,[fQtyProcessedLineTotExclNoDisc]
      ,[fQtyProcessedLineTaxAmount]
      ,[fQtyProcessedLineTaxAmountNoDisc]
      ,[fUnitPriceExclForeign]
      ,[fUnitPriceInclForeign]
      ,[fUnitCostForeign]
      ,[fAddCostForeign]
      ,[fQuantityLineTotInclForeign]
      ,[fQuantityLineTotExclForeign]
      ,[fQuantityLineTotInclNoDiscForeign]
      ,[fQuantityLineTotExclNoDiscForeign]
      ,[fQuantityLineTaxAmountForeign]
      ,[fQuantityLineTaxAmountNoDiscForeign]
      ,[fQtyChangeLineTotInclForeign]
      ,[fQtyChangeLineTotExclForeign]
      ,[fQtyChangeLineTotInclNoDiscForeign]
      ,[fQtyChangeLineTotExclNoDiscForeign]
      ,[fQtyChangeLineTaxAmountForeign]
      ,[fQtyChangeLineTaxAmountNoDiscForeign]
      ,[fQtyToProcessLineTotInclForeign]
      ,[fQtyToProcessLineTotExclForeign]
      ,[fQtyToProcessLineTotInclNoDiscForeign]
      ,[fQtyToProcessLineTotExclNoDiscForeign]
      ,[fQtyToProcessLineTaxAmountForeign]
      ,[fQtyToProcessLineTaxAmountNoDiscForeign]
      ,[fQtyLastProcessLineTotInclForeign]
      ,[fQtyLastProcessLineTotExclForeign]
      ,[fQtyLastProcessLineTotInclNoDiscForeign]
      ,[fQtyLastProcessLineTotExclNoDiscForeign]
      ,[fQtyLastProcessLineTaxAmountForeign]
      ,[fQtyLastProcessLineTaxAmountNoDiscForeign]
      ,[fQtyProcessedLineTotInclForeign]
      ,[fQtyProcessedLineTotExclForeign]
      ,[fQtyProcessedLineTotInclNoDiscForeign]
      ,[fQtyProcessedLineTotExclNoDiscForeign]
      ,[fQtyProcessedLineTaxAmountForeign]
      ,[fQtyProcessedLineTaxAmountNoDiscForeign]
      ,[iLineRepID]
      ,[iLineProjectID]
      ,[iLedgerAccountID]
      ,[iModule]
      ,[bChargeCom]
      ,[bIsLotItem]
      ,[iLotID]
      ,[cLotNumber]
      ,[dLotExpiryDate]
      ,[iMFPID]
      ,[iLineID]
      ,[iLinkedLineID]
      ,[fQtyLinkedUsed]
      ,[_btblInvoiceLines_iBranchID]
      ,[_btblInvoiceLines_dCreatedDate]
      ,[_btblInvoiceLines_dModifiedDate]
      ,[_btblInvoiceLines_iCreatedBranchID]
      ,[_btblInvoiceLines_iModifiedBranchID]
      ,[_btblInvoiceLines_iCreatedAgentID]
      ,[_btblInvoiceLines_iModifiedAgentID]
      ,[_btblInvoiceLines_iChangeSetID]
      ,[fUnitPriceInclOrig]
      ,[fUnitPriceExclOrig]
      ,[fUnitPriceInclForeignOrig]
      ,[fUnitPriceExclForeignOrig]
      ,[iDeliveryMethodID]
      ,[fQtyDeliver]
      ,[dDeliveryDate]
      ,[iDeliveryStatus]
      ,[fQtyForDelivery]
      ,[bPromotionApplied]
      ,[fPromotionPriceExcl]
      ,[fPromotionPriceIncl]
      ,[cPromotionCode]
      ,[iSOLinkedPOLineID]
      ,[fLength]
      ,[fWidth]
      ,[fHeight]
      ,[iPieces]
      ,[iPiecesToProcess]
      ,[iPiecesLastProcess]
      ,[iPiecesProcessed]
      ,[iPiecesReserved]
      ,[iPiecesDeliver]
      ,[iPiecesForDelivery]
      ,[fQuantityUR]
      ,[fQtyChangeUR]
      ,[fQtyToProcessUR]
      ,[fQtyLastProcessUR]
      ,[fQtyProcessedUR]
      ,[fQtyReservedUR]
      ,[fQtyReservedChangeUR]
      ,[fQtyDeliverUR]
      ,[fQtyForDeliveryUR]
      ,[fQtyLinkedUsedUR]
      ,[iPiecesLinkedUsed]
      ,[iSalesWhseID]
      ,[_btblInvoiceLines_Checksum]
      ,[bReverseChargeApplied]
      ,[fRecommendedRetailPrice]
      ,[UOMStockingUnitCode]
      ,[UOMUnitCode]
      ,[UOMfStockingQuantity]
      ,[UOMfStockingQtyChange]
      ,[UOMfStockingQtyToProcess]
      ,[UOMfStockingQtyLastProcess]
      ,[UOMfStockingQtyProcessed]
      ,[UOMfStockingQtyReserved]
      ,[UOMfStockingUnitCost]
      ,[UOMfStockingUnitPriceExcl]
      ,[UOMfStockingUnitPriceIncl]
      ,[UOMfStockingUnitPriceExclForeign]
      ,[UOMfStockingUnitPriceInclForeign]
      ,[StockLink]
      ,[Code]
      ,[Description_1]
      ,[Description_2]
      ,[Description_3]
      ,[ItemGroup]
      ,[Pack]
      ,[TTI]
      ,[TTC]
      ,[TTG]
      ,[TTR]
      ,[Bar_Code]
      ,[Re_Ord_Lvl]
      ,[Re_Ord_Qty]
      ,[Min_Lvl]
      ,[Max_Lvl]
      ,[AveUCst]
      ,[LatUCst]
      ,[LowUCst]
      ,[HigUCst]
      ,[StdUCst]
      ,[Qty_On_Hand]
      ,[LGrvCount]
      ,[ServiceItem]
      ,[ItemActive]
      ,[ReservedQty]
      ,[QtyOnPO]
      ,[QtyOnSO]
      ,[WhseItem]
      ,[SerialItem]
      ,[DuplicateSN]
      ,[StrictSN]
      ,[BomCode]
      ,[SMtrxCol]
      ,[PMtrxCol]
      ,[JobQty]
      ,[cModel]
      ,[cRevision]
      ,[cComponent]
      ,[dDateReleased]
      ,[iBinLocationID]
      ,[dStkitemTimeStamp]
      ,[iInvSegValue1ID]
      ,[iInvSegValue2ID]
      ,[iInvSegValue3ID]
      ,[iInvSegValue4ID]
      ,[iInvSegValue5ID]
      ,[iInvSegValue6ID]
      ,[iInvSegValue7ID]
      ,[cExtDescription]
      ,[cSimpleCode]
      ,[bCommissionItem]
      ,[MFPQty]
      ,[bLotItem]
      ,[iLotStatus]
      ,[bLotMustExpire]
      ,[iItemCostingMethod]
      ,[fItemLastGRVCost]
      ,[iEUCommodityID]
      ,[iEUSupplementaryUnitID]
      ,[fNetMass]
      ,[iUOMStockingUnitID]
      ,[iUOMDefPurchaseUnitID]
      ,[iUOMDefSellUnitID]
      ,[StkItem_iBranchID]
      ,[StkItem_dCreatedDate]
      ,[StkItem_dModifiedDate]
      ,[StkItem_iCreatedBranchID]
      ,[StkItem_iModifiedBranchID]
      ,[StkItem_iCreatedAgentID]
      ,[StkItem_iModifiedAgentID]
      ,[fStockGPPercent]
      ,[StkItem_iChangeSetID]
      ,[bAllowNegStock]
      ,[fQtyToDeliver]
      ,[StkItem_fLeadDays]
      ,[cEachDescription]
      ,[cMeasurement]
      ,[fBuyLength]
      ,[fBuyWidth]
      ,[fBuyHeight]
      ,[fBuyArea]
      ,[fBuyVolume]
      ,[cBuyWeight]
      ,[cBuyUnit]
      ,[fSellLength]
      ,[fSellWidth]
      ,[fSellHeight]
      ,[fSellArea]
      ,[fSellVolume]
      ,[cSellWeight]
      ,[cSellUnit]
      ,[bOverrideSell]
      ,[bUOMItem]
      ,[bDimensionItem]
      ,[iBuyingAgentID]
      ,[bVASItem]
      ,[bAirtimeItem]
      ,[fIBTQtyToIssue]
      ,[fIBTQtyToReceive]
      ,[StkItem_Checksum]
      ,[bSyncToSOT]
      ,[bImportedServices]
      ,[ufIIKgs]
      ,[DefaultDeliveryAddressID]
      ,[DefaultDeliveryAddCode]
      ,[DefaultDeliveryAddDescr]
      ,[DefaultDeliveryAdd1]
      ,[DefaultDeliveryAdd2]
      ,[DefaultDeliveryAdd3]
      ,[DefaultDeliveryAdd4]
      ,[DefaultDeliveryAdd5]
      ,[DefaultDeliveryAddPC]
      ,[DafaultDeliveryAddContact1]
      ,[DefaultDeliveryAddContact2]
      ,[DefaultDeliveryAddTel1]
      ,[DefaultDeliveryAddTel2]
      ,[DefaultDeliveryAddCell]
      ,[DefaultDeliveryAddFax]
      ,[DefaultDeliveryAddEmail]
      ,[DeliveryAdd1ID]
      ,[DeliveryAdd1Code]
      ,[DeliveryAdd1Descr]
      ,[DeliveryAdd1Line1]
      ,[DeliveryAdd1Line2]
      ,[DeliveryAdd1Line3]
      ,[DeliveryAdd1Line4]
      ,[DeliveryAdd1Line5]
      ,[DeliveryAdd1PC]
      ,[DeliveryAdd1Contact1]
      ,[DeliveryAdd1Contact2]
      ,[DeliveryAdd1Tel1]
      ,[DeliveryAdd1Tel2]
      ,[DeliveryAdd1Cell]
      ,[DeliveryAdd1Fax]
      ,[DeliveryAdd1Email]
      ,[DeliveryAdd2ID]
      ,[DeliveryAdd2Code]
      ,[DeliveryAdd2Descr]
      ,[DeliveryAdd2Line1]
      ,[DeliveryAdd2Line2]
      ,[DeliveryAdd2Line3]
      ,[DeliveryAdd2Line4]
      ,[DeliveryAdd2Line5]
      ,[DeliveryAdd2PC]
      ,[DeliveryAdd2Contact1]
      ,[DeliveryAdd2Contact2]
      ,[DeliveryAdd2Tel1]
      ,[DeliveryAdd2Tel2]
      ,[DeliveryAdd2Cell]
      ,[DeliveryAdd2Fax]
      ,[DeliveryAdd2Email]
      ,[DefaultSupplierLink]
      ,[DefaultSupplierCode]
      ,[DefaultSupplierName]
      ,[DefaultSupplierItemCode]
      ,[fMinOrderQuantity]
      ,[TaxType]
      ,[cJobCode]
      ,[WarehouseID]
      ,[WarehouseCode]
      ,[WarehouseName]
      ,[WhseMst_iBranchID]
      ,[AutoIndex]
      ,[DocType]
      ,[DocVersion]
      ,[DocState]
      ,[DocFlag]
      ,[OrigDocID]
      ,[InvNumber]
      ,[GrvNumber]
      ,[GrvID]
      ,[AccountID]
      ,[Description]
      ,[InvDate]
      ,[OrderDate]
      ,[DueDate]
      ,[DeliveryDate]
      ,[TaxInclusive]
      ,[Email_Sent]
      ,[Address1]
      ,[Address2]
      ,[Address3]
      ,[Address4]
      ,[Address5]
      ,[Address6]
      ,[PAddress1]
      ,[PAddress2]
      ,[PAddress3]
      ,[PAddress4]
      ,[PAddress5]
      ,[PAddress6]
      ,[DelMethodID]
      ,[DocRepID]
      ,[OrderNum]
      ,[DeliveryNote]
      ,[InvDisc]
      ,[InvDiscReasonID]
      ,[Message1]
      ,[Message2]
      ,[Message3]
      ,[ProjectID]
      ,[TillID]
      ,[POSAmntTendered]
      ,[POSChange]
      ,[GrvSplitFixedCost]
      ,[GrvSplitFixedAmnt]
      ,[OrderStatusID]
      ,[OrderPriorityID]
      ,[ExtOrderNum]
      ,[ForeignCurrencyID]
      ,[InvDiscAmnt]
      ,[InvDiscAmntEx]
      ,[InvTotExclDEx]
      ,[InvTotTaxDEx]
      ,[InvTotInclDEx]
      ,[InvTotExcl]
      ,[InvTotTax]
      ,[InvTotIncl]
      ,[OrdDiscAmnt]
      ,[OrdDiscAmntEx]
      ,[OrdTotExclDEx]
      ,[OrdTotTaxDEx]
      ,[OrdTotInclDEx]
      ,[OrdTotExcl]
      ,[OrdTotTax]
      ,[OrdTotIncl]
      ,[bUseFixedPrices]
      ,[iDocPrinted]
      ,[iINVNUMAgentID]
      ,[fExchangeRate]
      ,[fGrvSplitFixedAmntForeign]
      ,[fInvDiscAmntForeign]
      ,[fInvDiscAmntExForeign]
      ,[fInvTotExclDExForeign]
      ,[fInvTotTaxDExForeign]
      ,[fInvTotInclDExForeign]
      ,[fInvTotExclForeign]
      ,[fInvTotTaxForeign]
      ,[fInvTotInclForeign]
      ,[fOrdDiscAmntForeign]
      ,[fOrdDiscAmntExForeign]
      ,[fOrdTotExclDExForeign]
      ,[fOrdTotTaxDExForeign]
      ,[fOrdTotInclDExForeign]
      ,[fOrdTotExclForeign]
      ,[fOrdTotTaxForeign]
      ,[fOrdTotInclForeign]
      ,[cTaxNumber]
      ,[cAccountName]
      ,[iProspectID]
      ,[iOpportunityID]
      ,[InvTotRounding]
      ,[OrdTotRounding]
      ,[fInvTotForeignRounding]
      ,[fOrdTotForeignRounding]
      ,[bInvRounding]
      ,[iInvSettlementTermsID]
      ,[cSettlementTermInvMsg]
      ,[iOrderCancelReasonID]
      ,[iLinkedDocID]
      ,[bLinkedTemplate]
      ,[InvTotInclExRounding]
      ,[OrdTotInclExRounding]
      ,[fInvTotInclForeignExRounding]
      ,[fOrdTotInclForeignExRounding]
      ,[iEUNoTCID]
      ,[iPOAuthStatus]
      ,[iPOIncidentID]
      ,[iSupervisorID]
      ,[iMergedDocID]
      ,[InvNum_iBranchID]
      ,[InvNum_dCreatedDate]
      ,[InvNum_dModifiedDate]
      ,[InvNum_iCreatedBranchID]
      ,[InvNum_iModifiedBranchID]
      ,[InvNum_iCreatedAgentID]
      ,[InvNum_iModifiedAgentID]
      ,[InvNum_iChangeSetID]
      ,[iDocEmailed]
      ,[fDepositAmountForeign]
      ,[fRefundAmount]
      ,[bTaxPerLine]
      ,[fDepositAmountTotal]
      ,[fDepositAmountUnallocated]
      ,[fDepositAmountNew]
      ,[fDepositAmountTotalForeign]
      ,[fDepositAmountUnallocatedForeign]
      ,[fRefundAmountForeign]
      ,[KeepAsideCollectionDate]
      ,[KeepAsideExpiryDate]
      ,[cContact]
      ,[cTelephone]
      ,[cFax]
      ,[cEmail]
      ,[cCellular]
      ,[imgOrderSignature]
      ,[iInsuranceState]
      ,[cAuthorisedBy]
      ,[cClaimNumber]
      ,[cPolicyNumber]
      ,[dIncidentDate]
      ,[cExcessAccName]
      ,[cExcessAccCont1]
      ,[cExcessAccCont2]
      ,[fExcessAmt]
      ,[fExcessPct]
      ,[fExcessExclusive]
      ,[fExcessInclusive]
      ,[fExcessTax]
      ,[fAddChargeExclusive]
      ,[fAddChargeTax]
      ,[fAddChargeInclusive]
      ,[fAddChargeExclusiveForeign]
      ,[fAddChargeTaxForeign]
      ,[fAddChargeInclusiveForeign]
      ,[fOrdAddChargeExclusive]
      ,[fOrdAddChargeTax]
      ,[fOrdAddChargeInclusive]
      ,[fOrdAddChargeExclusiveForeign]
      ,[fOrdAddChargeTaxForeign]
      ,[fOrdAddChargeInclusiveForeign]
      ,[iInvoiceSplitDocID]
      ,[cGIVNumber]
      ,[bIsDCOrder]
      ,[iDCBranchID]
      ,[iSalesBranchID]
      ,[InvNum_Checksum]
      ,[bIDFProccessed]
      ,[iImportDeclarationID]
      ,[bSBSI]
      ,[cPermitNumber]
      ,[iStateID]
      ,[DCLink]
      ,[Account]
      ,[Name]
      ,[Title]
      ,[Init]
      ,[Contact_Person]
      ,[Physical1]
      ,[Physical2]
      ,[Physical3]
      ,[Physical4]
      ,[Physical5]
      ,[PhysicalPC]
      ,[Addressee]
      ,[Post1]
      ,[Post2]
      ,[Post3]
      ,[Post4]
      ,[Post5]
      ,[PostPC]
      ,[Delivered_To]
      ,[Telephone]
      ,[Telephone2]
      ,[Fax1]
      ,[Fax2]
      ,[AccountTerms]
      ,[CT]
      ,[Tax_Number]
      ,[Registration]
      ,[Credit_Limit]
      ,[RepID]
      ,[Interest_Rate]
      ,[Discount]
      ,[On_Hold]
      ,[BFOpenType]
      ,[EMail]
      ,[BankLink]
      ,[BranchCode]
      ,[BankAccNum]
      ,[BankAccType]
      ,[AutoDisc]
      ,[DiscMtrxRow]
      ,[MainAccLink]
      ,[CashDebtor]
      ,[DCBalance]
      ,[CheckTerms]
      ,[UseEmail]
      ,[iIncidentTypeID]
      ,[iBusTypeID]
      ,[iBusClassID]
      ,[iCountryID]
      ,[iAgentID]
      ,[dTimeStamp]
      ,[cAccDescription]
      ,[cWebPage]
      ,[iClassID]
      ,[iAreasID]
      ,[cBankRefNr]
      ,[iCurrencyID]
      ,[bStatPrint]
      ,[bStatEmail]
      ,[cStatEmailPass]
      ,[bForCurAcc]
      ,[fForeignBalance]
      ,[bTaxPrompt]
      ,[iARPriceListNameID]
      ,[iSettlementTermsID]
      ,[bSourceDocPrint]
      ,[bSourceDocEmail]
      ,[iEUCountryID]
      ,[iDefTaxTypeID]
      ,[bCODAccount]
      ,[Client_iBranchID]
      ,[Client_dCreatedDate]
      ,[Client_dModifiedDate]
      ,[Client_iCreatedBranchID]
      ,[Client_iModifiedBranchID]
      ,[Client_iCreatedAgentID]
      ,[Client_iModifiedAgentID]
      ,[Client_iChangeSetID]
      ,[iAgeingTermID]
      ,[bElecDocAcceptance]
      ,[iBankDetailType]
      ,[cBankAccHolder]
      ,[cIDNumber]
      ,[cPassportNumber]
      ,[bInsuranceCustomer]
      ,[cBankCode]
      ,[cSwiftCode]
      ,[iSPQueueID]
      ,[bCustomerZoneEnabled]
      ,[Client_Checksum]
      ,[iTaxState]
      ,[RepCode]
      ,[RepName]
      ,[TillNo]
      ,[ProjectCode]
      ,[ProjectName]
      ,[ActiveProject]
      ,[ProjectDescription]
      ,[Group]
      ,[GroupDescription]
      ,[Area]
      ,[AreaDescription]
      ,[CustomerRepName]
      ,[CustomerRepCode]
      ,[BankName]
      ,[MasterAccount]
      ,[MasterAccountName]
      ,[IncidentType]
      ,[BusinessType]
      ,[BusClassification]
      ,[CountryName]
      ,[AgentName]
      ,[AgentFirstName]
      ,[AgentLastName]
      ,[CurrencyCode]
      ,[CurrencyDescription]
      ,[cCurrencySymbol]
      ,[OrdCurrencySym]
      ,[cBinLocationName]
      ,[StatusDescription]
      ,[QtyOutstanding]
      ,[UOMStockingQtyOutstanding]
      ,[DocumentStateDesc]
      ,[LineItem]
      ,[DocFlagDesc]
      ,[ExPr1]
      ,[InPr1]
      ,[ExPr2]
      ,[InPr2]
      ,[ExPr3]
      ,[InPr3]
      ,[CancelReasonCode]
      ,[CancelReason]
      ,[PriorityDescription]
      ,[OpportunityNumber]
      ,[UOMUnit_Qty_On_Hand]
      ,[cProductReference]
      ,[Stock_LeadDays]
      ,[StockingUnit]
      ,[DimensionDescription]
      ,[Comment]
    """
    