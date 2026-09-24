-- Missing Database Tables for HMS
-- =============================================================
-- These tables exist in VB6 but are not in the SQL Server database.
-- Execute these scripts to create the missing tables.
-- Generated: 2026-09-23
-- =============================================================

-- HallBill: Banquet billing table
CREATE TABLE HallBill (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    BillNo VARCHAR(20) NOT NULL,
    EventCode VARCHAR(20),
    HallCode VARCHAR(20),
    GuestCode VARCHAR(20),
    BillDate DATETIME DEFAULT GETDATE(),
    TotalAmount DECIMAL(18,2) DEFAULT 0,
    PaidAmount DECIMAL(18,2) DEFAULT 0,
    Balance DECIMAL(18,2) DEFAULT 0,
    Status VARCHAR(20) DEFAULT 'PENDING',
    U_Name VARCHAR(50),
    U_EntDt DATETIME DEFAULT GETDATE(),
    U_AE VARCHAR(1) DEFAULT 'A'
);
CREATE INDEX IX_HallBill_BillNo ON HallBill(BillNo);
CREATE INDEX IX_HallBill_GuestCode ON HallBill(GuestCode);
CREATE INDEX IX_HallBill_Status ON HallBill(Status);

-- CateringBook: Banquet catering booking
CREATE TABLE CateringBook (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    BookNo VARCHAR(20) NOT NULL,
    EventCode VARCHAR(20),
    GuestCode VARCHAR(20),
    BookDate DATETIME DEFAULT GETDATE(),
    NoOfGuests INT DEFAULT 0,
    TotalAmount DECIMAL(18,2) DEFAULT 0,
    Status VARCHAR(20) DEFAULT 'PENDING',
    U_Name VARCHAR(50),
    U_EntDt DATETIME DEFAULT GETDATE(),
    U_AE VARCHAR(1) DEFAULT 'A'
);
CREATE INDEX IX_CateringBook_BookNo ON CateringBook(BookNo);

-- EventMast: Event master
CREATE TABLE EventMast (
    Code VARCHAR(20) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Venue VARCHAR(100),
    Capacity INT DEFAULT 0,
    Rate DECIMAL(18,2) DEFAULT 0,
    Active BIT DEFAULT 1,
    U_Name VARCHAR(50),
    U_EntDt DATETIME DEFAULT GETDATE(),
    U_AE VARCHAR(1) DEFAULT 'A'
);

-- BanquetSundry: Banquet sundry heads
CREATE TABLE BanquetSundry (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    EventCode VARCHAR(20),
    HeadName VARCHAR(100),
    Amount DECIMAL(18,2) DEFAULT 0,
    BillNo VARCHAR(20),
    U_Name VARCHAR(50),
    U_EntDt DATETIME DEFAULT GETDATE(),
    U_AE VARCHAR(1) DEFAULT 'A'
);

-- TelCall: Telephone call records
CREATE TABLE TelCall (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Extension VARCHAR(20),
    CallDate DATETIME DEFAULT GETDATE(),
    CallDuration INT DEFAULT 0,
    DialedNo VARCHAR(20),
    CallType VARCHAR(20),
    Amount DECIMAL(18,2) DEFAULT 0,
    U_Name VARCHAR(50),
    U_EntDt DATETIME DEFAULT GETDATE(),
    U_AE VARCHAR(1) DEFAULT 'A'
);
CREATE INDEX IX_TelCall_CallDate ON TelCall(CallDate);

-- Extension: PBX extension data
CREATE TABLE Extension (
    Code VARCHAR(20) PRIMARY KEY,
    Name VARCHAR(100),
    Department VARCHAR(50),
    Active BIT DEFAULT 1,
    U_Name VARCHAR(50),
    U_EntDt DATETIME DEFAULT GETDATE(),
    U_AE VARCHAR(1) DEFAULT 'A'
);

-- SmartCard: Smart card transactions
CREATE TABLE SmartCard (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    CardNo VARCHAR(20) NOT NULL,
    GuestCode VARCHAR(20),
    TransactionType VARCHAR(20),
    Amount DECIMAL(18,2) DEFAULT 0,
    Balance DECIMAL(18,2) DEFAULT 0,
    TransactionDate DATETIME DEFAULT GETDATE(),
    U_Name VARCHAR(50),
    U_EntDt DATETIME DEFAULT GETDATE(),
    U_AE VARCHAR(1) DEFAULT 'A'
);
CREATE INDEX IX_SmartCard_CardNo ON SmartCard(CardNo);

-- RewardPoint: Guest reward points
CREATE TABLE RewardPoint (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    GuestCode VARCHAR(20),
    Points DECIMAL(18,2) DEFAULT 0,
    TransactionType VARCHAR(20),
    Amount DECIMAL(18,2) DEFAULT 0,
    TransactionDate DATETIME DEFAULT GETDATE(),
    U_Name VARCHAR(50),
    U_EntDt DATETIME DEFAULT GETDATE(),
    U_AE VARCHAR(1) DEFAULT 'A'
);
CREATE INDEX IX_RewardPoint_GuestCode ON RewardPoint(GuestCode);

-- BookingInquiry: Booking inquiry log
CREATE TABLE BookingInquiry (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    InquiryDate DATETIME DEFAULT GETDATE(),
    GuestName VARCHAR(100),
    PhoneNo VARCHAR(20),
    ArrivalDate DATETIME,
    DepartureDate DATETIME,
    NoOfGuests INT DEFAULT 0,
    Status VARCHAR(20) DEFAULT 'OPEN',
    U_Name VARCHAR(50),
    U_EntDt DATETIME DEFAULT GETDATE(),
    U_AE VARCHAR(1) DEFAULT 'A'
);
CREATE INDEX IX_BookingInquiry_InquiryDate ON BookingInquiry(InquiryDate);

-- Additional tables referenced in VB6 (from mdi_menu.json analysis)
-- DoorLockConfig: Door lock settings
CREATE TABLE DoorLockConfig (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    RoomNo VARCHAR(20) NOT NULL,
    LockCode VARCHAR(50),
    GuestName VARCHAR(100),
    AccessExpiry DATETIME,
    Active BIT DEFAULT 1,
    UpdatedDate DATETIME DEFAULT GETDATE()
);
CREATE INDEX IX_DoorLockConfig_RoomNo ON DoorLockConfig(RoomNo);

-- SMSLog: SMS message log
CREATE TABLE SMSLog (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    PhoneNo VARCHAR(20),
    Message TEXT,
    Status VARCHAR(20) DEFAULT 'SENT',
    Template VARCHAR(50),
    SentDate DATETIME DEFAULT GETDATE()
);
CREATE INDEX IX_SMSLog_PhoneNo ON SMSLog(PhoneNo);
CREATE INDEX IX_SMSLog_SentDate ON SMSLog(SentDate);

-- EInvoice: E-invoice records
CREATE TABLE EInvoice (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    InvoiceNo VARCHAR(20) NOT NULL,
    GuestCode VARCHAR(20),
    BaseAmount DECIMAL(18,2) DEFAULT 0,
    CGST DECIMAL(18,2) DEFAULT 0,
    SGST DECIMAL(18,2) DEFAULT 0,
    TotalAmount DECIMAL(18,2) DEFAULT 0,
    IRN VARCHAR(50),
    QRData VARCHAR(500),
    Submitted BIT DEFAULT 0,
    InvoiceDate DATETIME DEFAULT GETDATE(),
    U_Name VARCHAR(50),
    U_EntDt DATETIME DEFAULT GETDATE(),
    U_AE VARCHAR(1) DEFAULT 'A'
);
CREATE INDEX IX_EInvoice_InvoiceNo ON EInvoice(InvoiceNo);

-- GuestFolioAmend: Guest folio amendment log
CREATE TABLE GuestFolioAmend (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    FolioNo VARCHAR(20),
    AmendDate DATETIME DEFAULT GETDATE(),
    OldValue VARCHAR(500),
    NewValue VARCHAR(500),
    U_Name VARCHAR(50),
    U_EntDt DATETIME DEFAULT GETDATE()
);

-- NightAuditLog: Night audit log details
CREATE TABLE NightAuditLogDetail (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    AuditDate DATETIME DEFAULT GETDATE(),
    ModuleName VARCHAR(50),
    Action VARCHAR(50),
    Details VARCHAR(500),
    U_Name VARCHAR(50)
);

-- DataTransferLog: Multi-site data transfer log
CREATE TABLE DataTransferLog (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    TransferDate DATETIME DEFAULT GETDATE(),
    SiteCode VARCHAR(10),
    TransferType VARCHAR(20),
    RecordsCount INT DEFAULT 0,
    Status VARCHAR(20) DEFAULT 'PENDING',
    Details VARCHAR(500)
);

-- BillWiseOutstanding: Bill-wise outstanding report data
CREATE TABLE BillWiseOutstanding (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    DocId VARCHAR(20),
    GuestCode VARCHAR(20),
    BillDate DATETIME,
    Amount DECIMAL(18,2),
    PaidAmount DECIMAL(18,2) DEFAULT 0,
    Balance DECIMAL(18,2),
    DueDate DATETIME
);

-- Print output confirmation
SELECT 'Missing tables created successfully.' AS Result;
