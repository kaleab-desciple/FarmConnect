export interface Harvest {
    $schema:     string;
    $id:         string;
    title:       string;
    definitions: Definitions;
}

export interface Definitions {
    HarvestEvent:             HarvestEvent;
    HarvestBatch:             HarvestBatch;
    HarvestBatchContribution: HarvestBatchContribution;
    BatchQCReport:            BatchQcReport;
    BatchQCReportV2:          BatchQcReport;
    Sample:                   Sample;
    LabProvider:              LabProvider;
    Certification:            Certification;
    QCGradeRule:              QCGradeRule;
    AuditEvent:               AuditEvent;
    Harvest:                  HarvestClass;
}

export interface AuditEvent {
    type:                 Type;
    properties:           AuditEventProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface AuditEventProperties {
    id:                  CreatedAt;
    event_type:          EntityID;
    entity_type:         EntityID;
    entity_id:           EntityID;
    payload:             Payload;
    payload_hash:        Payload;
    previous_event_hash: Payload;
    user_id:             Payload;
    signature:           Payload;
    created_at:          CreatedAt;
}

export interface CreatedAt {
    type:   Type;
    format: Format;
}

export enum Format {
    Date = "date",
    DateTime = "date-time",
    UUID = "uuid",
}

export enum Type {
    Boolean = "boolean",
    Null = "null",
    Number = "number",
    Object = "object",
    String = "string",
}

export interface EntityID {
    type: Type;
}

export interface Payload {
    type: Type[];
}

export interface BatchQcReport {
    type:                 Type;
    properties:           BatchQCReportProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface BatchQCReportProperties {
    id:          CreatedAt;
    batch_id:    CreatedAt;
    lab_id:      Payload;
    tested_at:   CreatedAt;
    metrics:     Payload;
    passed:      EntityID;
    report_url:  Payload;
    signed_hash: Payload;
    notes:       Payload;
    created_at:  CreatedAt;
    sample_id?:  SampleID;
    grade?:      Payload;
    verified?:   Verified;
}

export interface SampleID {
    type:   Type[];
    format: Format;
}

export interface Verified {
    type:    Type;
    default: boolean;
}

export interface Certification {
    type:                 Type;
    properties:           CertificationProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface CertificationProperties {
    id:               CreatedAt;
    harvest_batch_id: CreatedAt;
    issuer:           EntityID;
    cert_type:        CERTType;
    cert_number:      Payload;
    valid_from:       CreatedAt;
    valid_to:         CreatedAt;
    cert_url:         Payload;
    signed_hash:      Payload;
    metadata:         Payload;
    created_at:       CreatedAt;
}

export interface CERTType {
    type: Type;
    enum: string[];
}

export interface HarvestClass {
    type:                 Type;
    properties:           HarvestProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface HarvestProperties {
    id:                 CreatedAt;
    farmer_id:          EntityID;
    crop_cycle_id:      SampleID;
    field_id:           CreatedAt;
    harvest_date:       CreatedAt;
    quantity_harvested: EntityID;
    unit:               Payload;
    quality_grade:      Payload;
    notes:              Payload;
    metadata:           Payload;
    created_at:         CreatedAt;
    updated_at:         CreatedAt;
}

export interface HarvestBatch {
    type:                 Type;
    properties:           HarvestBatchProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface HarvestBatchProperties {
    id:                   CreatedAt;
    batch_code:           BatchCode;
    aggregator_id:        Payload;
    notes:                Payload;
    metadata:             Payload;
    status:               Status;
    aggregated_weight_kg: Payload;
    moisture_avg:         Payload;
    sealed_at:            SampleID;
    sealed_by:            Payload;
    seal_evidence:        Payload;
    lineage_hash:         Payload;
    lineage_signature:    Payload;
    created_at:           CreatedAt;
    updated_at:           CreatedAt;
    contributions:        Contributions;
}

export interface BatchCode {
    type:        Type;
    description: string;
}

export interface Contributions {
    type:  string;
    items: EntityID;
}

export interface Status {
    type:    Type;
    default: string;
}

export interface HarvestBatchContribution {
    type:                 Type;
    properties:           HarvestBatchContributionProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface HarvestBatchContributionProperties {
    id:                    CreatedAt;
    harvest_batch_id:      CreatedAt;
    harvest_event_id:      CreatedAt;
    farmer_id:             EntityID;
    contributed_weight_kg: EntityID;
    reported_moisture_pct: Payload;
    created_at:            CreatedAt;
}

export interface HarvestEvent {
    type:                 Type;
    properties:           HarvestEventProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface HarvestEventProperties {
    id:                  CreatedAt;
    farm_id:             BatchCode;
    field_id:            BatchCode;
    crop_cycle_id:       CropCycleID;
    collected_by:        CollectedBy;
    harvested_at:        HarvestedAt;
    gross_weight_kg:     BatchCode;
    moisture_pct:        MoisturePct;
    loss_kg:             LossKg;
    photos:              Photos;
    weighbridge_receipt: Payload;
    location:            Payload;
    notes:               Payload;
    created_at:          CreatedAt;
    updated_at:          CreatedAt;
}

export interface CollectedBy {
    type:        Type[];
    description: string;
}

export interface CropCycleID {
    type:        Type[];
    format:      Format;
    description: string;
}

export interface HarvestedAt {
    type:        Type;
    format:      Format;
    description: string;
}

export interface LossKg {
    type:    Type;
    default: number;
}

export interface MoisturePct {
    type:    Type[];
    minimum: number;
    maximum: number;
}

export interface Photos {
    type:  string[];
    items: EntityID;
}

export interface LabProvider {
    type:                 Type;
    properties:           LabProviderProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface LabProviderProperties {
    id:         CreatedAt;
    name:       EntityID;
    public_key: Payload;
    metadata:   Payload;
    created_at: CreatedAt;
}

export interface QCGradeRule {
    type:                 Type;
    properties:           QCGradeRuleProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface QCGradeRuleProperties {
    id:         CreatedAt;
    commodity:  EntityID;
    grade:      EntityID;
    rules:      Contributions;
    is_active:  Verified;
    created_at: CreatedAt;
    updated_at: CreatedAt;
}

export interface Sample {
    type:                 Type;
    properties:           SampleProperties;
    required:             string[];
    additionalProperties: boolean;
}

export interface SampleProperties {
    id:               CreatedAt;
    sample_code:      EntityID;
    harvest_batch_id: CreatedAt;
    collected_by:     Payload;
    collected_at:     SampleID;
    sample_points:    Payload;
    photos:           Photos;
    chain_of_custody: Payload;
    submitted_to_lab: Verified;
    created_at:       CreatedAt;
}
