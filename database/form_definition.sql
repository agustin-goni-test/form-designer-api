-- create schema
CREATE SCHEMA IF NOT EXISTS form_definition;

-- forms: logical form definitions
CREATE TABLE form_definition.forms (
    id               SERIAL PRIMARY KEY,
    key              TEXT    UNIQUE NOT NULL,    -- human-readable identifier
    name             TEXT    NOT NULL,
    description      TEXT,
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now()
);

-- Table comment
COMMENT ON TABLE form_definition.forms IS 'Logical form definitions. Each form can have multiple versions.';

-- Column comments
COMMENT ON COLUMN form_definition.forms.id IS 'Auto-incrementing primary key identifier';
COMMENT ON COLUMN form_definition.forms.key IS 'Human-readable identifier for the form (e.g. "contact_form")';
COMMENT ON COLUMN form_definition.forms.name IS 'Display name of the form';
COMMENT ON COLUMN form_definition.forms.description IS 'Detailed description of the form';
COMMENT ON COLUMN form_definition.forms.created_at IS 'Timestamp when the form was created';
COMMENT ON COLUMN form_definition.forms.updated_at IS 'Timestamp when the form was last updated';



-- form_versions: specific versions of a form
CREATE TABLE form_definition.form_versions (
    id               SERIAL PRIMARY KEY,
    form_id          INTEGER NOT NULL REFERENCES form_definition.forms(id) ON DELETE CASCADE,
    version_number   INTEGER NOT NULL,
    key              TEXT    NOT NULL,           -- version key (e.g. "v1", "2025-10")
    schema           JSONB  NOT NULL,            -- JSON definition for this version
    is_active        BOOLEAN DEFAULT FALSE,
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE(form_id, version_number),
    UNIQUE(form_id, key)
);

-- Table comments
COMMENT ON TABLE form_definition.form_versions IS 'Specific versions of a form, each with its own JSON schema definition.';

-- Column comments
COMMENT ON COLUMN form_definition.form_versions.id IS 'Auto-incrementing primary key identifier';
COMMENT ON COLUMN form_definition.form_versions.form_id IS 'Foreign key referencing the parent form';
COMMENT ON COLUMN form_definition.form_versions.version_number IS 'Sequential version number for the form';
COMMENT ON COLUMN form_definition.form_versions.key IS 'Human-readable version key (e.g. "v1", "2025-10")';
COMMENT ON COLUMN form_definition.form_versions.schema IS 'JSON schema definition for this form version';
COMMENT ON COLUMN form_definition.form_versions.is_active IS 'Indicates if this version is the currently active version for the form';
COMMENT ON COLUMN form_definition.form_versions.created_at IS 'Timestamp when the form version was created';
COMMENT ON COLUMN form_definition.form_versions.updated_at IS 'Timestamp when the form version was last updated';



-- workflows: named workflows (sequence containers)
CREATE TABLE form_definition.workflows (
    id               SERIAL PRIMARY KEY,
    key              TEXT    UNIQUE NOT NULL,    -- human-readable workflow key
    name             TEXT    NOT NULL,
    description      TEXT,
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now()
);

-- Table comment
COMMENT ON TABLE form_definition.workflows IS 'Named workflows, which are sequences of form versions.';

-- Column comments
COMMENT ON COLUMN form_definition.workflows.id IS 'Auto-incrementing primary key identifier';
COMMENT ON COLUMN form_definition.workflows.key IS 'Human-readable identifier for the workflow (e.g. "user_registration")';
COMMENT ON COLUMN form_definition.workflows.name IS 'Display name of the workflow';
COMMENT ON COLUMN form_definition.workflows.description IS 'Detailed description of the workflow';
COMMENT ON COLUMN form_definition.workflows.created_at IS 'Timestamp when the workflow was created';
COMMENT ON COLUMN form_definition.workflows.updated_at IS 'Timestamp when the workflow was last updated';


-- workflow_steps: ordered steps composing a workflow (references a specific form_version)
CREATE TABLE form_definition.workflow_steps (
    id                SERIAL PRIMARY KEY,
    workflow_id       INTEGER NOT NULL REFERENCES form_definition.workflows(id) ON DELETE CASCADE,
    form_version_id   INTEGER NOT NULL REFERENCES form_definition.form_versions(id),
    step_order        INTEGER NOT NULL,          -- 1,2,3... defines order in workflow
    is_optional       BOOLEAN DEFAULT FALSE,
    created_at        TIMESTAMPTZ DEFAULT now(),
    updated_at        TIMESTAMPTZ DEFAULT now(),
    UNIQUE(workflow_id, step_order)
);

-- Table comment
COMMENT ON TABLE form_definition.workflow_steps IS 'Ordered steps composing a workflow, each referencing a specific form version.';

-- Column comments
COMMENT ON COLUMN form_definition.workflow_steps.id IS 'Auto-incrementing primary key identifier';
COMMENT ON COLUMN form_definition.workflow_steps.workflow_id IS 'Foreign key referencing the parent workflow';
COMMENT ON COLUMN form_definition.workflow_steps.form_version_id IS 'Foreign key referencing the specific form version for this step';
COMMENT ON COLUMN form_definition.workflow_steps.step_order IS 'Defines the order of this step within the workflow (1,2,3...)';
COMMENT ON COLUMN form_definition.workflow_steps.is_optional IS 'Indicates if this step is optional within the workflow';
COMMENT ON COLUMN form_definition.workflow_steps.created_at IS 'Timestamp when the workflow step was created';
COMMENT ON COLUMN form_definition.workflow_steps.updated_at IS 'Timestamp when the workflow step was last updated';


-- Component base definitions
CREATE TABLE form_definition.components (
    id SERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,              -- "EmailBox", "PhoneBox", etc.
    name TEXT NOT NULL,                    -- "Email Input Field"
    description TEXT,
    base_component_id INTEGER REFERENCES form_definition.components(id)
        ON DELETE RESTRICT                 -- Prevent deleting a base component if others depend on it
        ON UPDATE CASCADE,                 -- If ID changes (rare), update children
    category TEXT NOT NULL,                -- "input", "choice", "layout", "custom"
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Table comments
COMMENT ON TABLE form_definition.components IS 'Base definitions for reusable form components (that can inherit from standard components).';

-- Column comments
COMMENT ON COLUMN form_definition.components.id IS 'Auto-incrementing primary key identifier';
COMMENT ON COLUMN form_definition.components.key IS 'Human-readable identifier for the component (e.g. "EmailBox")';
COMMENT ON COLUMN form_definition.components.name IS 'Display name of the component';
COMMENT ON COLUMN form_definition.components.description IS 'Component description';
COMMENT ON COLUMN form_definition.components.base_component_id IS 'Specifies the id of the base component this component inherits from, if any';
COMMENT ON COLUMN form_definition.components.category IS 'Category of the component (e.g. "input", "choice", "layout", "custom")';
COMMENT ON COLUMN form_definition.components.created_at IS 'Timestamp when the component was created';
COMMENT ON COLUMN form_definition.components.updated_at IS 'Timestamp when the component was last updated';


-- Component versions (for evolution)
CREATE TABLE form_definition.component_versions (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES form_definition.components(id),
    version_number INTEGER NOT NULL,
    definition JSONB NOT NULL,         -- Full merged definition
    default_props JSONB,               -- Optional defaults at this version
    validation_config JSONB,           -- Validation rules for this version
    service_bindings JSONB,            -- Behavior endpoints for this version
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Table comments
COMMENT ON TABLE form_definition.component_versions IS 'Base definitions for reusable form component versions';

-- Column comments
COMMENT ON COLUMN form_definition.component_versions.id IS 'Auto-incrementing primary key identifier';
COMMENT ON COLUMN form_definition.component_versions.component_id IS 'Foreign key referencing the parent component';
COMMENT ON COLUMN form_definition.component_versions.version_number IS 'Sequential version number for the component';
COMMENT ON COLUMN form_definition.component_versions.definition IS 'Full component definition stored as JSON (consolidates all properties)';
COMMENT ON COLUMN form_definition.component_versions.default_props IS 'Default properties for the component stored as JSON';
COMMENT ON COLUMN form_definition.component_versions.validation_config IS 'Built-in validation rules for the component stored as JSON';
COMMENT ON COLUMN form_definition.component_versions.service_bindings IS 'Default service endpoints for the component stored as JSON';
COMMENT ON COLUMN form_definition.component_versions.is_active IS 'Indicates if this version is the currently active version for the component';
COMMENT ON COLUMN form_definition.component_versions.created_at IS 'Timestamp when the component version was created';


-- Explicit service definitions
CREATE TABLE form_definition.form_services (
    id SERIAL PRIMARY KEY,
    form_version_id INTEGER REFERENCES form_definition.form_versions(id),
    service_type TEXT NOT NULL, -- 'entry', 'exit', 'validation'
    service_endpoint TEXT NOT NULL,
    http_method TEXT DEFAULT 'POST',
    configuration JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(form_version_id, service_type)
);

-- Table comments
COMMENT ON TABLE form_definition.form_services IS 'Explicit service definitions for form versions, such as entry, exit, and validation services.';

-- Column comments
COMMENT ON COLUMN form_definition.form_services.id IS 'Auto-incrementing primary key identifier';
COMMENT ON COLUMN form_definition.form_services.form_version_id IS 'Foreign key referencing the associated form version';
COMMENT ON COLUMN form_definition.form_services.service_type IS 'Type of service (e.g. "entry", "exit", "validation")';
COMMENT ON COLUMN form_definition.form_services.service_endpoint IS 'URL endpoint for the service';
COMMENT ON COLUMN form_definition.form_services.http_method IS 'HTTP method to use for the service (default: POST)';
COMMENT ON COLUMN form_definition.form_services.configuration IS 'Additional configuration for the service stored as JSON';
COMMENT ON COLUMN form_definition.form_services.created_at IS 'Timestamp when the service definition was created';
COMMENT ON COLUMN form_definition.form_services.updated_at IS 'Timestamp when the service definition was last updated';


-- useful indexes (optional)
CREATE INDEX idx_form_versions_form_id ON form_definition.form_versions(form_id);
CREATE INDEX idx_workflow_steps_workflow_id ON form_definition.workflow_steps(workflow_id);
CREATE INDEX idx_component_versions_component_id ON form_definition.component_versions(component_id);
