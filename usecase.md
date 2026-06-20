```mermaid
%% Campus Lost & Found - Clean Use Case Diagram

flowchart LR
    %% Left actor
    User["Student/Staff"]:::actor
    
    %% Right actor
    Admin["Admin"]:::actor

    %% Center use cases in a subgraph for better layout
    subgraph UseCases["Use Cases"]
        UC1(["Register Account"])
        UC2(["Login"])
        UC3(["Report Lost Item"])
        UC4(["View Lost Items"])
        UC5(["Claim Found Item"])
        UC6(["Manage Items"])
        UC7(["Approve Reports"])
    end

    %% Relationships
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5

    Admin --> UC4
    Admin --> UC6
    Admin --> UC7

    %% Styling
    classDef actor fill:#FFFFE0,stroke:#333,stroke-width:2px,color:#000,shape:rect,font-size:18px
    classDef usecase fill:#E0F7FF,stroke:#333,stroke-width:1px,color:#000,rx:25,ry:25,font-size:16px
    class UC1,UC2,UC3,UC4,UC5,UC6,UC7 usecase
