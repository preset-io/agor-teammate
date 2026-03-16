# Preset Architecture — Mermaid Diagrams

Reference diagrams for the Preset Architect. Use these in conversations, on boards, or when answering architecture questions.

---

## 1. Core Platform — Request Path

```mermaid
flowchart LR
    User([User / Browser])
    CLI([superset-sup CLI])
    SDK([api-clients SDK])

    User --> GW
    CLI --> SDK --> GW

    subgraph Preset Platform
        GW[api-gateway<br/><i>Multi-tenant router</i>]
        MGR[manager<br/><i>Account mgmt, billing,<br/>workspace CRUD</i>]
        SS[superset-shell<br/><i>Auth, feature flags,<br/>copilot, analytics</i>]
        SP[superset-private<br/><i>Preset fork: embedding,<br/>SSO, MCP service</i>]
        OSS[apache/superset<br/><i>Upstream OSS</i>]
    end

    GW --> MGR
    MGR --> SS
    SS --> SP
    SP --> OSS

    style OSS fill:#20A6C9,stroke:#333,color:#fff
    style SS fill:#f7931e,stroke:#333,color:#fff
    style MGR fill:#722ed1,stroke:#333,color:#fff
    style GW fill:#1668dc,stroke:#333,color:#fff
```

---

## 2. The Shell Pattern

```mermaid
flowchart TB
    subgraph "Shell Pattern (Core Architectural Pattern)"
        direction TB
        OSS1[apache/superset<br/><i>Open source</i>] -->|private fork| SP1[superset-private<br/><i>Enterprise features</i>]
        SP1 -->|wrapped by| SS1[superset-shell<br/><i>Preset config layer</i>]

        OSS2[agor<br/><i>Open source</i>] -->|wrapped by| AS1[agor-shell<br/><i>Preset config layer</i>]
    end

    note1[Shell adds:<br/>• Auth / SSO<br/>• Feature flags<br/>• Analytics events<br/>• Customer config<br/>• AI/Copilot integration]

    SS1 -.- note1
    AS1 -.- note1
```

---

## 3. Three Deployment Models

```mermaid
flowchart TB
    subgraph SaaS["SaaS (Multi-tenant)"]
        direction LR
        S1[Preset manages everything]
        S2[Shared K8s clusters]
        S3[app.preset.io]
        S1 --- S2 --- S3
    end

    subgraph MPC["MPC (Managed Private Cloud)"]
        direction LR
        M1[Customer runs mpc-init]
        M2[Preset manages infra<br/>in customer's cloud]
        M3[Dedicated cluster]
        M1 --> M2 --> M3
    end

    subgraph PCS["PCS (Private Cloud Superset)"]
        direction LR
        P1[Customer pulls preset-pcs<br/>Helm charts + images]
        P2[Customer deploys<br/>to own infra]
        P3[Optional FIPS images]
        P1 --> P2 --- P3
    end

    style SaaS fill:#52c41a22,stroke:#52c41a
    style MPC fill:#1668dc22,stroke:#1668dc
    style PCS fill:#722ed122,stroke:#722ed1
```

---

## 4. Infrastructure — Terraform 3-Tier + Deployment

```mermaid
flowchart TB
    subgraph Terraform["Terraform Stack"]
        TMR[terraform-modules-resources<br/><i>DEPRECATED — atomic modules</i>]
        TMS[terraform-modules-services<br/><i>Composable: EKS, RDS, VPC...</i>]
        TLE[terraform-live-envs<br/><i>Per-environment configs</i>]

        TMR -.->|avoided| TMS
        TMS --> TLE
    end

    TLE -->|Atlantis CI/CD| INFRA[AWS / GCP Infrastructure]

    subgraph Deployment["GitOps Delivery"]
        DI[docker-images<br/><i>15+ custom images</i>]
        HLM[helm<br/><i>Charts + per-cluster config</i>]
        ARGO[argocd<br/><i>App-of-apps GitOps</i>]
        SDP[service-deploy-pipeline<br/><i>Jenkins → K8s via Helm</i>]

        DI --> HLM --> ARGO
        SDP --> ARGO
    end

    INFRA --> K8S[K8s Clusters]
    ARGO --> K8S

    subgraph Clusters["What Runs in K8s"]
        SS2[superset-shell]
        MGR2[manager]
        GW2[api-gateway]
        CJ[cronjobs]
        PB[platform-broker]
    end

    K8S --> Clusters

    style TMR fill:#ff000022,stroke:#ff4d4f
    style TMS fill:#52c41a22,stroke:#52c41a
    style TLE fill:#52c41a22,stroke:#52c41a
```

---

## 5. What "A Superset Cluster" Provisions

```mermaid
flowchart TB
    subgraph cluster["Superset Cluster (app-stack)"]
        EKS[EKS Cluster<br/><i>VPC, 3 AZs, ASGs</i>]

        subgraph data["Data Layer"]
            RDS1[(RDS PostgreSQL<br/><b>superset</b> metadata)]
            RDS2[(RDS PostgreSQL<br/><b>examples</b> sample data)]
            R1[(ElastiCache Redis<br/><b>ss</b> Celery broker)]
            R2[(ElastiCache Redis<br/><b>sc</b> Result cache)]
        end

        subgraph storage["Storage"]
            S1[(S3 Encrypted<br/>Query results<br/><i>15-day expiry</i>)]
            S2[(S3 Encrypted<br/>Thumbnails<br/><i>15-day expiry</i>)]
        end

        subgraph network["Networking"]
            VPC[VPC Peering<br/><i>→ DevOps VPN</i><br/><i>→ DevOps EKS</i>]
            DNS[Route53<br/><i>Public + Private zones</i>]
        end

        subgraph monitoring["Monitoring"]
            DD[Datadog users<br/><i>on both Postgres</i>]
            IAM[IAM Superset user<br/><i>S3, service perms</i>]
        end
    end

    style cluster fill:#1668dc11,stroke:#1668dc
```

---

## 6. Release & Deployment Pipeline

```mermaid
flowchart LR
    RM[release-maker<br/><i>Cuts release branch</i>]
    SP3[superset-private]
    SS3[superset-shell]

    RM --> SP3
    RM --> SS3

    SP3 --> BUILD[Docker Build<br/><i>docker-images</i>]
    SS3 --> BUILD

    BUILD --> REG[Container Registry]
    REG --> HELM2[Helm Charts]
    HELM2 --> ARGO2[ArgoCD]

    ARGO2 --> STG[Staging]
    STG -->|promoted| PROD[Production]

    EPH[ephemeral-env-pipeline] --> SBX[Sandbox]

    style RM fill:#f7931e22,stroke:#f7931e
    style PROD fill:#52c41a22,stroke:#52c41a
    style STG fill:#d4a01722,stroke:#d4a017
```

---

## 7. MPC Customer Onboarding

```mermaid
sequenceDiagram
    participant Customer
    participant mpc-init
    participant TLE as terraform-live-envs
    participant ArgoCD
    participant Superset

    Customer->>mpc-init: Run setup (TF module or shell script)
    mpc-init->>Customer: Creates IAM role + service account
    Note over Customer: PresetMPCAdminV2 role granted

    TLE->>Customer: Provision cluster in customer's cloud
    TLE->>ArgoCD: Register new cluster
    ArgoCD->>Customer: Deploy Helm charts
    Customer->>Superset: Superset running in customer's VPC
```

---

## 8. AI / Agent Layer

```mermaid
flowchart TB
    subgraph "In-Product AI (Superset)"
        COP[Copilot<br/><i>superset-shell/preset/copilot/</i>]
        MCP_SVC[MCP Service<br/><i>superset-private/mcp_service/</i>]
        AAL[ai-assist-lib<br/><i>Shared AI utilities</i>]
        COP --> MCP_SVC
        COP --> AAL
    end

    subgraph "Agor Platform"
        AGOR[agor<br/><i>Session orchestration</i>]
        ASHELL[agor-shell<br/><i>Preset config</i>]
        AASST[agor-assistant<br/><i>Agent framework</i>]
        SMCP[slack-mcp<br/><i>Slack integration</i>]
        AGOR --> ASHELL
        AGOR --> AASST
        AGOR --> SMCP
    end

    subgraph "AI Tooling"
        BIRD[birdsai]
        TMCP[testmcpy<br/><i>MCP test framework</i>]
        PROM[promptimize<br/><i>Prompt eval</i>]
        AI18[ai18n<br/><i>AI translation</i>]
    end

    MCP_SVC -.->|MCP protocol| AGOR
    TMCP -.->|tests| MCP_SVC
```

---

## 9. Data Pipeline (from DatAgor Board)

```mermaid
flowchart LR
    subgraph Sources
        HS[HubSpot]
        GH[GitHub]
        RC[Recurly]
        PD[Pendo]
        SC[Shortcut]
    end

    subgraph ETL
        SEG[Segment]
        FT[Fivetran]
    end

    Sources --> SEG --> BQ[(BigQuery)]
    Sources --> FT --> BQ

    subgraph Transform
        DBT[dbt]
        AF[Airflow]
    end

    BQ --> DBT --> AF --> BQ

    BQ --> SS4[Superset Dashboards<br/><i>eating our own cooking</i>]

    BQ --> HT[Hightouch] --> HS

    style BQ fill:#4285F4,stroke:#333,color:#fff
    style DBT fill:#FF6B4A,stroke:#333
    style SS4 fill:#20A6C9,stroke:#333,color:#fff
```

---

## Usage Notes

These diagrams can be:
- Rendered on Agor boards (markdown objects support mermaid)
- Referenced in conversations when answering architecture questions
- Updated as the architecture evolves
- Copied into PRDs, TRDs, or design docs
