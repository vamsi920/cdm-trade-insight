// Mock CDM (Common Domain Model) outputs for testing
export interface CDMOutput {
  id: string;
  tradeId: string;
  eventId: string;
  timestamp: string;
  cdmVersion: string;
  businessEvent: {
    eventType: string;
    eventDate: string;
    effectiveDate: string;
    party: string[];
  };
  tradableProduct: {
    productIdentifier: string;
    productType: string;
    economicTerms: {
      notional: {
        amount: number;
        currency: string;
      };
      effectiveDate: string;
      terminationDate: string;
      calculationPeriodDates?: {
        effectiveDate: string;
        terminationDate: string;
        calculationPeriodFrequency: string;
      };
      paymentDates?: {
        paymentFrequency: string;
        paymentDatesAdjustments: string;
      };
      interestRateStream?: {
        payerPartyReference: string;
        receiverPartyReference: string;
        calculationPeriodAmount: {
          calculation: {
            notionalSchedule: {
              notionalStepSchedule: {
                initialValue: number;
                currency: string;
              };
            };
            fixedRateSchedule?: {
              initialValue: number;
            };
            floatingRateCalculation?: {
              floatingRateIndex: string;
              indexTenor: string;
              spread?: number;
            };
          };
        };
      }[];
    };
  };
  transferHistory: {
    transfer: {
      quantity: {
        amount: number;
        currency: string;
      };
      asset: {
        productIdentifier: string;
      };
      payerReceiver: {
        payer: string;
        receiver: string;
      };
      settlementDate: string;
    }[];
  };
}

export interface DRRReport {
  id: string;
  tradeId: string;
  eventId: string;
  reportDate: string;
  reportType: "EMIR" | "CFTC" | "MAS" | "JFSA";
  jurisdiction: string;
  reportingParty: string;
  counterparty: string;
  reportingStatus: "NEW" | "MODIFY" | "CANCEL" | "ERROR";
  validationResults: {
    status: "PASS" | "FAIL" | "WARNING";
    errors: string[];
    warnings: string[];
  };
  reportFields: {
    uti: string;
    upi?: string;
    notionalAmount: number;
    notionalCurrency: string;
    executionTimestamp: string;
    effectiveDate: string;
    maturityDate: string;
    underlyingAsset?: string;
    fixedRate?: number;
    floatingRateIndex?: string;
    spread?: number;
    paymentFrequency?: string;
    settlementCurrency?: string;
    collateralization:
      | "UNCOLLATERALIZED"
      | "PARTIALLY_COLLATERALIZED"
      | "FULLY_COLLATERALIZED";
    compressionExercised: boolean;
    priceData?: {
      price: number;
      priceType: string;
      priceNotation: string;
    };
  };
  submissionDetails: {
    submissionTimestamp: string;
    messageId: string;
    batchId?: string;
    acknowledgmentStatus: "ACK" | "NACK" | "PENDING";
    acknowledgmentTimestamp?: string;
  };
}

export const mockCDMOutputs: CDMOutput[] = [
  {
    id: "cdm-001",
    tradeId: "TRD-2024-001",
    eventId: "evt-001",
    timestamp: "2024-01-15T10:30:00Z",
    cdmVersion: "5.12.0",
    businessEvent: {
      eventType: "Execution",
      eventDate: "2024-01-15",
      effectiveDate: "2024-01-15",
      party: ["Sample Bank", "Counterparty A"],
    },
    tradableProduct: {
      productIdentifier: "IRS-USD-SOFR-5Y",
      productType: "InterestRateSwap",
      economicTerms: {
        notional: {
          amount: 50000000,
          currency: "USD",
        },
        effectiveDate: "2024-01-15",
        terminationDate: "2029-01-15",
        calculationPeriodDates: {
          effectiveDate: "2024-01-15",
          terminationDate: "2029-01-15",
          calculationPeriodFrequency: "3M",
        },
        paymentDates: {
          paymentFrequency: "3M",
          paymentDatesAdjustments: "ModifiedFollowing",
        },
        interestRateStream: [
          {
            payerPartyReference: "Sample Bank",
            receiverPartyReference: "Counterparty A",
            calculationPeriodAmount: {
              calculation: {
                notionalSchedule: {
                  notionalStepSchedule: {
                    initialValue: 50000000,
                    currency: "USD",
                  },
                },
                fixedRateSchedule: {
                  initialValue: 0.0325,
                },
              },
            },
          },
          {
            payerPartyReference: "Counterparty A",
            receiverPartyReference: "Sample Bank",
            calculationPeriodAmount: {
              calculation: {
                notionalSchedule: {
                  notionalStepSchedule: {
                    initialValue: 50000000,
                    currency: "USD",
                  },
                },
                floatingRateCalculation: {
                  floatingRateIndex: "USD-SOFR-OIS Compound",
                  indexTenor: "3M",
                  spread: 0.005,
                },
              },
            },
          },
        ],
      },
    },
    transferHistory: {
      transfer: [],
    },
  },
  {
    id: "cdm-002",
    tradeId: "TRD-2024-001",
    eventId: "evt-003",
    timestamp: "2024-06-20T14:15:00Z",
    cdmVersion: "5.12.0",
    businessEvent: {
      eventType: "Amendment",
      eventDate: "2024-06-20",
      effectiveDate: "2024-06-20",
      party: ["Sample Bank", "Counterparty A"],
    },
    tradableProduct: {
      productIdentifier: "IRS-USD-SOFR-5Y",
      productType: "InterestRateSwap",
      economicTerms: {
        notional: {
          amount: 45000000,
          currency: "USD",
        },
        effectiveDate: "2024-01-15",
        terminationDate: "2029-01-15",
        calculationPeriodDates: {
          effectiveDate: "2024-01-15",
          terminationDate: "2029-01-15",
          calculationPeriodFrequency: "3M",
        },
        paymentDates: {
          paymentFrequency: "3M",
          paymentDatesAdjustments: "ModifiedFollowing",
        },
        interestRateStream: [
          {
            payerPartyReference: "Sample Bank",
            receiverPartyReference: "Counterparty A",
            calculationPeriodAmount: {
              calculation: {
                notionalSchedule: {
                  notionalStepSchedule: {
                    initialValue: 45000000,
                    currency: "USD",
                  },
                },
                fixedRateSchedule: {
                  initialValue: 0.0325,
                },
              },
            },
          },
          {
            payerPartyReference: "Counterparty A",
            receiverPartyReference: "Sample Bank",
            calculationPeriodAmount: {
              calculation: {
                notionalSchedule: {
                  notionalStepSchedule: {
                    initialValue: 45000000,
                    currency: "USD",
                  },
                },
                floatingRateCalculation: {
                  floatingRateIndex: "USD-SOFR-OIS Compound",
                  indexTenor: "3M",
                  spread: 0.005,
                },
              },
            },
          },
        ],
      },
    },
    transferHistory: {
      transfer: [],
    },
  },
];

export const mockDRRReports: DRRReport[] = [
  {
    id: "drr-001",
    tradeId: "TRD-2024-001",
    eventId: "evt-001",
    reportDate: "2024-01-16",
    reportType: "EMIR",
    jurisdiction: "EU",
    reportingParty: "Sample Bank",
    counterparty: "Counterparty A",
    reportingStatus: "NEW",
    validationResults: {
      status: "PASS",
      errors: [],
      warnings: [
        "Minor formatting issue in field 2.78 - corrected automatically",
      ],
    },
    reportFields: {
      uti: "UTI-SB-2024-001-001",
      upi: "UPI-IRS-USD-SOFR",
      notionalAmount: 50000000,
      notionalCurrency: "USD",
      executionTimestamp: "2024-01-15T10:30:00Z",
      effectiveDate: "2024-01-15",
      maturityDate: "2029-01-15",
      fixedRate: 3.25,
      floatingRateIndex: "USD-SOFR-OIS Compound",
      spread: 0.5,
      paymentFrequency: "3M",
      settlementCurrency: "USD",
      collateralization: "FULLY_COLLATERALIZED",
      compressionExercised: false,
      priceData: {
        price: 3.25,
        priceType: "InterestRate",
        priceNotation: "PercentageOfNotional",
      },
    },
    submissionDetails: {
      submissionTimestamp: "2024-01-16T09:15:00Z",
      messageId: "MSG-EMIR-20240116-001",
      batchId: "BATCH-20240116-001",
      acknowledgmentStatus: "ACK",
      acknowledgmentTimestamp: "2024-01-16T09:16:23Z",
    },
  },
  {
    id: "drr-002",
    tradeId: "TRD-2024-001",
    eventId: "evt-003",
    reportDate: "2024-06-21",
    reportType: "EMIR",
    jurisdiction: "EU",
    reportingParty: "Sample Bank",
    counterparty: "Counterparty A",
    reportingStatus: "MODIFY",
    validationResults: {
      status: "PASS",
      errors: [],
      warnings: [],
    },
    reportFields: {
      uti: "UTI-SB-2024-001-001",
      upi: "UPI-IRS-USD-SOFR",
      notionalAmount: 45000000,
      notionalCurrency: "USD",
      executionTimestamp: "2024-01-15T10:30:00Z",
      effectiveDate: "2024-01-15",
      maturityDate: "2029-01-15",
      fixedRate: 3.25,
      floatingRateIndex: "USD-SOFR-OIS Compound",
      spread: 0.5,
      paymentFrequency: "3M",
      settlementCurrency: "USD",
      collateralization: "FULLY_COLLATERALIZED",
      compressionExercised: false,
      priceData: {
        price: 3.25,
        priceType: "InterestRate",
        priceNotation: "PercentageOfNotional",
      },
    },
    submissionDetails: {
      submissionTimestamp: "2024-06-21T11:30:00Z",
      messageId: "MSG-EMIR-20240621-003",
      batchId: "BATCH-20240621-002",
      acknowledgmentStatus: "ACK",
      acknowledgmentTimestamp: "2024-06-21T11:31:45Z",
    },
  },
  {
    id: "drr-003",
    tradeId: "TRD-2024-002",
    eventId: "evt-005",
    reportDate: "2024-03-02",
    reportType: "CFTC",
    jurisdiction: "US",
    reportingParty: "Sample Bank",
    counterparty: "Counterparty B",
    reportingStatus: "NEW",
    validationResults: {
      status: "PASS",
      errors: [],
      warnings: [],
    },
    reportFields: {
      uti: "UTI-SB-2024-002-001",
      upi: "UPI-CDS-USD-CORP",
      notionalAmount: 25000000,
      notionalCurrency: "USD",
      executionTimestamp: "2024-03-01T15:45:00Z",
      effectiveDate: "2024-03-01",
      maturityDate: "2027-03-01",
      underlyingAsset: "XYZ Corp",
      settlementCurrency: "USD",
      collateralization: "PARTIALLY_COLLATERALIZED",
      compressionExercised: false,
      priceData: {
        price: 250,
        priceType: "CreditSpread",
        priceNotation: "BasisPoints",
      },
    },
    submissionDetails: {
      submissionTimestamp: "2024-03-02T08:20:00Z",
      messageId: "MSG-CFTC-20240302-001",
      acknowledgmentStatus: "ACK",
      acknowledgmentTimestamp: "2024-03-02T08:22:15Z",
    },
  },
];
