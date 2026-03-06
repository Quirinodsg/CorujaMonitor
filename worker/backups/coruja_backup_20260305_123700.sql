--
-- PostgreSQL database dump
--

\restrict 9WtFILhCaPdQFb7GJYmpobzOACliv5QhvOsI5WlR3zB7I8evhvuBz4Mjr0rtA2A

-- Dumped from database version 15.15
-- Dumped by pg_dump version 17.8 (Debian 17.8-0+deb13u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: coruja
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO coruja;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: coruja
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ai_analysis_logs; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.ai_analysis_logs (
    id integer NOT NULL,
    incident_id integer,
    analysis_type character varying(100) NOT NULL,
    input_data json,
    output_data json,
    model_used character varying(100),
    tokens_used integer,
    execution_time_ms integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.ai_analysis_logs OWNER TO coruja;

--
-- Name: ai_analysis_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.ai_analysis_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ai_analysis_logs_id_seq OWNER TO coruja;

--
-- Name: ai_analysis_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.ai_analysis_logs_id_seq OWNED BY public.ai_analysis_logs.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    user_id integer,
    tenant_id integer,
    action character varying(100) NOT NULL,
    resource_type character varying(50),
    resource_id integer,
    details json,
    ip_address character varying(50),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.audit_logs OWNER TO coruja;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO coruja;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: authentication_config; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.authentication_config (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    ldap_config json,
    saml_config json,
    oauth2_config json,
    azure_ad_config json,
    google_config json,
    okta_config json,
    mfa_config json,
    password_policy json,
    session_config json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.authentication_config OWNER TO coruja;

--
-- Name: authentication_config_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.authentication_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.authentication_config_id_seq OWNER TO coruja;

--
-- Name: authentication_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.authentication_config_id_seq OWNED BY public.authentication_config.id;


--
-- Name: auto_resolution_config; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.auto_resolution_config (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    auto_resolution_enabled boolean,
    require_approval_for_critical boolean,
    min_confidence_threshold double precision,
    min_success_rate_threshold double precision,
    cpu_auto_resolve boolean,
    cpu_max_risk_level character varying(20),
    memory_auto_resolve boolean,
    memory_max_risk_level character varying(20),
    disk_auto_resolve boolean,
    disk_max_risk_level character varying(20),
    service_auto_resolve boolean,
    service_max_risk_level character varying(20),
    network_auto_resolve boolean,
    network_max_risk_level character varying(20),
    allowed_hours_start integer,
    allowed_hours_end integer,
    allowed_days json,
    notify_before_execution boolean,
    notify_after_execution boolean,
    notification_channels json,
    max_executions_per_hour integer,
    max_executions_per_day integer,
    cooldown_minutes integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.auto_resolution_config OWNER TO coruja;

--
-- Name: auto_resolution_config_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.auto_resolution_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.auto_resolution_config_id_seq OWNER TO coruja;

--
-- Name: auto_resolution_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.auto_resolution_config_id_seq OWNED BY public.auto_resolution_config.id;


--
-- Name: custom_reports; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.custom_reports (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    user_id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    report_type character varying(50) NOT NULL,
    filters json,
    columns json,
    sort_by character varying(100),
    sort_order character varying(10),
    is_public boolean,
    is_favorite boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    last_generated_at timestamp with time zone
);


ALTER TABLE public.custom_reports OWNER TO coruja;

--
-- Name: custom_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.custom_reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.custom_reports_id_seq OWNER TO coruja;

--
-- Name: custom_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.custom_reports_id_seq OWNED BY public.custom_reports.id;


--
-- Name: incidents; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.incidents (
    id integer NOT NULL,
    sensor_id integer NOT NULL,
    severity character varying(20) NOT NULL,
    status character varying(20),
    title character varying(500) NOT NULL,
    description text,
    root_cause text,
    ai_analysis json,
    remediation_attempted boolean,
    remediation_successful boolean,
    created_at timestamp with time zone DEFAULT now(),
    resolved_at timestamp with time zone,
    acknowledged_at timestamp with time zone,
    acknowledged_by integer,
    acknowledgement_notes text,
    resolution_notes text
);


ALTER TABLE public.incidents OWNER TO coruja;

--
-- Name: incidents_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.incidents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.incidents_id_seq OWNER TO coruja;

--
-- Name: incidents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.incidents_id_seq OWNED BY public.incidents.id;


--
-- Name: knowledge_base; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.knowledge_base (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    problem_signature character varying(500) NOT NULL,
    sensor_type character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    problem_title character varying(500) NOT NULL,
    problem_description text NOT NULL,
    symptoms json,
    root_cause text NOT NULL,
    root_cause_confidence double precision,
    solution_description text NOT NULL,
    solution_steps json NOT NULL,
    solution_commands json,
    learned_from_incident_id integer,
    learned_from_user_id integer,
    times_matched integer,
    times_successful integer,
    success_rate double precision,
    auto_resolution_enabled boolean,
    requires_approval boolean,
    risk_level character varying(20),
    affected_os json,
    affected_versions json,
    prerequisites json,
    rollback_steps json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    last_matched_at timestamp with time zone
);


ALTER TABLE public.knowledge_base OWNER TO coruja;

--
-- Name: knowledge_base_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.knowledge_base_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.knowledge_base_id_seq OWNER TO coruja;

--
-- Name: knowledge_base_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.knowledge_base_id_seq OWNED BY public.knowledge_base.id;


--
-- Name: kubernetes_alert_rules; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.kubernetes_alert_rules (
    id integer NOT NULL,
    cluster_id integer,
    tenant_id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    alert_type character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    resource_type character varying(50),
    metric_name character varying(100) NOT NULL,
    operator character varying(20) NOT NULL,
    threshold double precision NOT NULL,
    duration integer DEFAULT 60,
    namespace_filter character varying(255),
    label_filter jsonb DEFAULT '{}'::jsonb,
    is_active boolean DEFAULT true,
    notify_email boolean DEFAULT true,
    notify_webhook boolean DEFAULT false,
    webhook_url character varying(500),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.kubernetes_alert_rules OWNER TO coruja;

--
-- Name: kubernetes_alert_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.kubernetes_alert_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kubernetes_alert_rules_id_seq OWNER TO coruja;

--
-- Name: kubernetes_alert_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.kubernetes_alert_rules_id_seq OWNED BY public.kubernetes_alert_rules.id;


--
-- Name: kubernetes_alerts; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.kubernetes_alerts (
    id integer NOT NULL,
    cluster_id integer NOT NULL,
    resource_id integer,
    alert_type character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    title character varying(255) NOT NULL,
    message text NOT NULL,
    resource_type character varying(50),
    resource_name character varying(255),
    namespace character varying(255),
    current_value double precision,
    threshold_value double precision,
    status character varying(20) DEFAULT 'active'::character varying,
    acknowledged_at timestamp without time zone,
    acknowledged_by integer,
    resolved_at timestamp without time zone,
    alert_metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.kubernetes_alerts OWNER TO coruja;

--
-- Name: kubernetes_alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.kubernetes_alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kubernetes_alerts_id_seq OWNER TO coruja;

--
-- Name: kubernetes_alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.kubernetes_alerts_id_seq OWNED BY public.kubernetes_alerts.id;


--
-- Name: kubernetes_clusters; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.kubernetes_clusters (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    probe_id integer,
    cluster_name character varying(255) NOT NULL,
    cluster_type character varying(50) NOT NULL,
    api_endpoint character varying(500) NOT NULL,
    auth_method character varying(50) NOT NULL,
    kubeconfig_content text,
    service_account_token text,
    ca_cert text,
    monitor_all_namespaces boolean,
    namespaces json,
    selected_resources json,
    collection_interval integer,
    is_active boolean,
    last_connection_test timestamp with time zone,
    connection_status character varying(50),
    connection_error text,
    total_nodes integer,
    total_pods integer,
    total_deployments integer,
    cluster_cpu_usage double precision,
    cluster_memory_usage double precision,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    last_collected_at timestamp with time zone
);


ALTER TABLE public.kubernetes_clusters OWNER TO coruja;

--
-- Name: kubernetes_clusters_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.kubernetes_clusters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kubernetes_clusters_id_seq OWNER TO coruja;

--
-- Name: kubernetes_clusters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.kubernetes_clusters_id_seq OWNED BY public.kubernetes_clusters.id;


--
-- Name: kubernetes_metrics; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.kubernetes_metrics (
    id integer NOT NULL,
    resource_id integer NOT NULL,
    cpu_usage double precision,
    memory_usage double precision,
    network_rx_bytes double precision,
    network_tx_bytes double precision,
    disk_usage double precision,
    status character varying(50),
    ready boolean,
    restart_count integer,
    "timestamp" timestamp with time zone DEFAULT now()
);


ALTER TABLE public.kubernetes_metrics OWNER TO coruja;

--
-- Name: kubernetes_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.kubernetes_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kubernetes_metrics_id_seq OWNER TO coruja;

--
-- Name: kubernetes_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.kubernetes_metrics_id_seq OWNED BY public.kubernetes_metrics.id;


--
-- Name: kubernetes_resources; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.kubernetes_resources (
    id integer NOT NULL,
    cluster_id integer NOT NULL,
    resource_type character varying(50) NOT NULL,
    resource_name character varying(255) NOT NULL,
    namespace character varying(255),
    uid character varying(255),
    labels json,
    annotations json,
    status character varying(50),
    phase character varying(50),
    ready boolean,
    metrics json,
    node_cpu_capacity double precision,
    node_memory_capacity double precision,
    node_cpu_usage double precision,
    node_memory_usage double precision,
    node_pod_count integer,
    node_pod_capacity integer,
    pod_cpu_usage double precision,
    pod_memory_usage double precision,
    pod_restart_count integer,
    pod_node_name character varying(255),
    desired_replicas integer,
    ready_replicas integer,
    available_replicas integer,
    updated_replicas integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    last_seen_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.kubernetes_resources OWNER TO coruja;

--
-- Name: kubernetes_resources_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.kubernetes_resources_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kubernetes_resources_id_seq OWNER TO coruja;

--
-- Name: kubernetes_resources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.kubernetes_resources_id_seq OWNED BY public.kubernetes_resources.id;


--
-- Name: learning_sessions; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.learning_sessions (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    incident_id integer NOT NULL,
    user_id integer NOT NULL,
    problem_description text NOT NULL,
    root_cause_identified text,
    solution_applied text NOT NULL,
    resolution_steps json,
    commands_used json,
    sensor_type character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    resolution_time_minutes integer,
    added_to_knowledge_base boolean,
    knowledge_base_id integer,
    confidence_score double precision,
    was_successful boolean,
    technician_notes text,
    created_at timestamp with time zone DEFAULT now(),
    learned_at timestamp with time zone
);


ALTER TABLE public.learning_sessions OWNER TO coruja;

--
-- Name: learning_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.learning_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.learning_sessions_id_seq OWNER TO coruja;

--
-- Name: learning_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.learning_sessions_id_seq OWNED BY public.learning_sessions.id;


--
-- Name: maintenance_windows; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.maintenance_windows (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    server_id integer,
    title character varying(255) NOT NULL,
    description text,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone NOT NULL,
    created_by integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.maintenance_windows OWNER TO coruja;

--
-- Name: maintenance_windows_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.maintenance_windows_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.maintenance_windows_id_seq OWNER TO coruja;

--
-- Name: maintenance_windows_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.maintenance_windows_id_seq OWNED BY public.maintenance_windows.id;


--
-- Name: metrics; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.metrics (
    id integer NOT NULL,
    sensor_id integer NOT NULL,
    value double precision NOT NULL,
    unit character varying(20),
    status character varying(20),
    "timestamp" timestamp with time zone NOT NULL,
    metadata json
);


ALTER TABLE public.metrics OWNER TO coruja;

--
-- Name: metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.metrics_id_seq OWNER TO coruja;

--
-- Name: metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.metrics_id_seq OWNED BY public.metrics.id;


--
-- Name: monthly_reports; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.monthly_reports (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    year integer NOT NULL,
    month integer NOT NULL,
    availability_percentage double precision,
    total_incidents integer,
    auto_resolved_incidents integer,
    sla_compliance double precision,
    report_data json,
    ai_summary text,
    generated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.monthly_reports OWNER TO coruja;

--
-- Name: monthly_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.monthly_reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.monthly_reports_id_seq OWNER TO coruja;

--
-- Name: monthly_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.monthly_reports_id_seq OWNED BY public.monthly_reports.id;


--
-- Name: probes; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.probes (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    name character varying(255) NOT NULL,
    token character varying(500) NOT NULL,
    is_active boolean,
    last_heartbeat timestamp with time zone,
    version character varying(50),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.probes OWNER TO coruja;

--
-- Name: probes_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.probes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.probes_id_seq OWNER TO coruja;

--
-- Name: probes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.probes_id_seq OWNED BY public.probes.id;


--
-- Name: remediation_logs; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.remediation_logs (
    id integer NOT NULL,
    incident_id integer NOT NULL,
    action_type character varying(100) NOT NULL,
    action_description text,
    before_state json,
    after_state json,
    success boolean NOT NULL,
    error_message text,
    executed_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.remediation_logs OWNER TO coruja;

--
-- Name: remediation_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.remediation_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.remediation_logs_id_seq OWNER TO coruja;

--
-- Name: remediation_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.remediation_logs_id_seq OWNED BY public.remediation_logs.id;


--
-- Name: resolution_attempts; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.resolution_attempts (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    incident_id integer NOT NULL,
    knowledge_base_id integer,
    problem_signature character varying(500) NOT NULL,
    solution_applied text NOT NULL,
    commands_executed json,
    status character varying(50) NOT NULL,
    success boolean,
    error_message text,
    execution_time_seconds double precision,
    state_before json,
    state_after json,
    requires_approval boolean,
    approved_by integer,
    approved_at timestamp with time zone,
    approval_notes text,
    technician_feedback text,
    feedback_rating integer,
    feedback_by integer,
    feedback_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    executed_at timestamp with time zone,
    completed_at timestamp with time zone
);


ALTER TABLE public.resolution_attempts OWNER TO coruja;

--
-- Name: resolution_attempts_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.resolution_attempts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resolution_attempts_id_seq OWNER TO coruja;

--
-- Name: resolution_attempts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.resolution_attempts_id_seq OWNED BY public.resolution_attempts.id;


--
-- Name: sensor_breach_history; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.sensor_breach_history (
    id integer NOT NULL,
    sensor_id integer,
    breach_start timestamp with time zone NOT NULL,
    breach_end timestamp with time zone,
    breach_value double precision,
    threshold_type character varying(20),
    incident_created boolean DEFAULT false,
    incident_id integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.sensor_breach_history OWNER TO coruja;

--
-- Name: sensor_breach_history_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.sensor_breach_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sensor_breach_history_id_seq OWNER TO coruja;

--
-- Name: sensor_breach_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.sensor_breach_history_id_seq OWNED BY public.sensor_breach_history.id;


--
-- Name: sensor_groups; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.sensor_groups (
    id integer NOT NULL,
    tenant_id integer,
    name character varying(255) NOT NULL,
    parent_id integer,
    description text,
    icon character varying(50) DEFAULT '📁'::character varying,
    color character varying(20),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.sensor_groups OWNER TO coruja;

--
-- Name: sensor_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.sensor_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sensor_groups_id_seq OWNER TO coruja;

--
-- Name: sensor_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.sensor_groups_id_seq OWNED BY public.sensor_groups.id;


--
-- Name: sensor_notes; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.sensor_notes (
    id integer NOT NULL,
    sensor_id integer NOT NULL,
    user_id integer NOT NULL,
    note text NOT NULL,
    status character varying(50) NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.sensor_notes OWNER TO coruja;

--
-- Name: sensor_notes_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.sensor_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sensor_notes_id_seq OWNER TO coruja;

--
-- Name: sensor_notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.sensor_notes_id_seq OWNED BY public.sensor_notes.id;


--
-- Name: sensors; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.sensors (
    id integer NOT NULL,
    server_id integer,
    name character varying(255) NOT NULL,
    sensor_type character varying(50) NOT NULL,
    config json,
    threshold_warning double precision,
    threshold_critical double precision,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    verification_status character varying(50) DEFAULT 'pending'::character varying,
    last_note text,
    last_note_by integer,
    last_note_at timestamp with time zone,
    collection_protocol character varying(20) DEFAULT 'wmi'::character varying,
    snmp_oid character varying(255),
    is_acknowledged boolean DEFAULT false,
    acknowledged_by integer,
    acknowledged_at timestamp with time zone,
    probe_id integer,
    group_id integer
);


ALTER TABLE public.sensors OWNER TO coruja;

--
-- Name: sensors_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.sensors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sensors_id_seq OWNER TO coruja;

--
-- Name: sensors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.sensors_id_seq OWNED BY public.sensors.id;


--
-- Name: servers; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.servers (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    probe_id integer NOT NULL,
    hostname character varying(255) NOT NULL,
    ip_address character varying(50),
    os_type character varying(50),
    os_version character varying(100),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    public_ip character varying(50),
    group_name character varying(255),
    tags json,
    device_type character varying(50) DEFAULT 'server'::character varying,
    monitoring_protocol character varying(20) DEFAULT 'wmi'::character varying,
    snmp_version character varying(10),
    snmp_community character varying(255),
    snmp_port integer DEFAULT 161,
    environment character varying(50) DEFAULT 'production'::character varying,
    monitoring_schedule json,
    wmi_username character varying(255),
    wmi_password_encrypted text,
    wmi_domain character varying(255),
    wmi_enabled boolean DEFAULT false,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.servers OWNER TO coruja;

--
-- Name: COLUMN servers.wmi_username; Type: COMMENT; Schema: public; Owner: coruja
--

COMMENT ON COLUMN public.servers.wmi_username IS 'Username for WMI remote access (e.g., Administrator or DOMAIN\user)';


--
-- Name: COLUMN servers.wmi_password_encrypted; Type: COMMENT; Schema: public; Owner: coruja
--

COMMENT ON COLUMN public.servers.wmi_password_encrypted IS 'Encrypted password for WMI access (use Fernet encryption)';


--
-- Name: COLUMN servers.wmi_domain; Type: COMMENT; Schema: public; Owner: coruja
--

COMMENT ON COLUMN public.servers.wmi_domain IS 'Windows domain for WMI authentication (optional)';


--
-- Name: COLUMN servers.wmi_enabled; Type: COMMENT; Schema: public; Owner: coruja
--

COMMENT ON COLUMN public.servers.wmi_enabled IS 'Enable WMI remote monitoring for this server';


--
-- Name: servers_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.servers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.servers_id_seq OWNER TO coruja;

--
-- Name: servers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.servers_id_seq OWNED BY public.servers.id;


--
-- Name: tenants; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.tenants (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    slug character varying(100) NOT NULL,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    notification_config json
);


ALTER TABLE public.tenants OWNER TO coruja;

--
-- Name: tenants_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.tenants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tenants_id_seq OWNER TO coruja;

--
-- Name: tenants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.tenants_id_seq OWNED BY public.tenants.id;


--
-- Name: threshold_config; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.threshold_config (
    id integer NOT NULL,
    tenant_id integer,
    breach_duration_seconds integer DEFAULT 600,
    flapping_window_seconds integer DEFAULT 300,
    flapping_threshold integer DEFAULT 3,
    cpu_breach_duration integer DEFAULT 600,
    memory_breach_duration integer DEFAULT 900,
    disk_breach_duration integer DEFAULT 1800,
    ping_breach_duration integer DEFAULT 180,
    service_breach_duration integer DEFAULT 120,
    network_breach_duration integer DEFAULT 600,
    suppress_during_maintenance boolean DEFAULT true,
    suppress_acknowledged boolean DEFAULT true,
    suppress_flapping boolean DEFAULT true,
    escalation_enabled boolean DEFAULT false,
    escalation_time_minutes integer DEFAULT 30,
    escalation_severity character varying(20) DEFAULT 'critical'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.threshold_config OWNER TO coruja;

--
-- Name: threshold_config_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.threshold_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.threshold_config_id_seq OWNER TO coruja;

--
-- Name: threshold_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.threshold_config_id_seq OWNED BY public.threshold_config.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: coruja
--

CREATE TABLE public.users (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    email character varying(255) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(255),
    role character varying(50),
    is_active boolean,
    language character varying(10),
    created_at timestamp with time zone DEFAULT now(),
    mfa_enabled boolean DEFAULT false,
    mfa_secret character varying(255),
    mfa_backup_codes json
);


ALTER TABLE public.users OWNER TO coruja;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: coruja
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO coruja;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coruja
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: ai_analysis_logs id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.ai_analysis_logs ALTER COLUMN id SET DEFAULT nextval('public.ai_analysis_logs_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: authentication_config id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.authentication_config ALTER COLUMN id SET DEFAULT nextval('public.authentication_config_id_seq'::regclass);


--
-- Name: auto_resolution_config id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.auto_resolution_config ALTER COLUMN id SET DEFAULT nextval('public.auto_resolution_config_id_seq'::regclass);


--
-- Name: custom_reports id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.custom_reports ALTER COLUMN id SET DEFAULT nextval('public.custom_reports_id_seq'::regclass);


--
-- Name: incidents id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.incidents ALTER COLUMN id SET DEFAULT nextval('public.incidents_id_seq'::regclass);


--
-- Name: knowledge_base id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.knowledge_base ALTER COLUMN id SET DEFAULT nextval('public.knowledge_base_id_seq'::regclass);


--
-- Name: kubernetes_alert_rules id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_alert_rules ALTER COLUMN id SET DEFAULT nextval('public.kubernetes_alert_rules_id_seq'::regclass);


--
-- Name: kubernetes_alerts id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_alerts ALTER COLUMN id SET DEFAULT nextval('public.kubernetes_alerts_id_seq'::regclass);


--
-- Name: kubernetes_clusters id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_clusters ALTER COLUMN id SET DEFAULT nextval('public.kubernetes_clusters_id_seq'::regclass);


--
-- Name: kubernetes_metrics id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_metrics ALTER COLUMN id SET DEFAULT nextval('public.kubernetes_metrics_id_seq'::regclass);


--
-- Name: kubernetes_resources id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_resources ALTER COLUMN id SET DEFAULT nextval('public.kubernetes_resources_id_seq'::regclass);


--
-- Name: learning_sessions id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.learning_sessions ALTER COLUMN id SET DEFAULT nextval('public.learning_sessions_id_seq'::regclass);


--
-- Name: maintenance_windows id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.maintenance_windows ALTER COLUMN id SET DEFAULT nextval('public.maintenance_windows_id_seq'::regclass);


--
-- Name: metrics id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.metrics ALTER COLUMN id SET DEFAULT nextval('public.metrics_id_seq'::regclass);


--
-- Name: monthly_reports id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.monthly_reports ALTER COLUMN id SET DEFAULT nextval('public.monthly_reports_id_seq'::regclass);


--
-- Name: probes id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.probes ALTER COLUMN id SET DEFAULT nextval('public.probes_id_seq'::regclass);


--
-- Name: remediation_logs id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.remediation_logs ALTER COLUMN id SET DEFAULT nextval('public.remediation_logs_id_seq'::regclass);


--
-- Name: resolution_attempts id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.resolution_attempts ALTER COLUMN id SET DEFAULT nextval('public.resolution_attempts_id_seq'::regclass);


--
-- Name: sensor_breach_history id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_breach_history ALTER COLUMN id SET DEFAULT nextval('public.sensor_breach_history_id_seq'::regclass);


--
-- Name: sensor_groups id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_groups ALTER COLUMN id SET DEFAULT nextval('public.sensor_groups_id_seq'::regclass);


--
-- Name: sensor_notes id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_notes ALTER COLUMN id SET DEFAULT nextval('public.sensor_notes_id_seq'::regclass);


--
-- Name: sensors id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensors ALTER COLUMN id SET DEFAULT nextval('public.sensors_id_seq'::regclass);


--
-- Name: servers id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.servers ALTER COLUMN id SET DEFAULT nextval('public.servers_id_seq'::regclass);


--
-- Name: tenants id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.tenants ALTER COLUMN id SET DEFAULT nextval('public.tenants_id_seq'::regclass);


--
-- Name: threshold_config id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.threshold_config ALTER COLUMN id SET DEFAULT nextval('public.threshold_config_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: ai_analysis_logs; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.ai_analysis_logs (id, incident_id, analysis_type, input_data, output_data, model_used, tokens_used, execution_time_ms, created_at) FROM stdin;
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.audit_logs (id, user_id, tenant_id, action, resource_type, resource_id, details, ip_address, created_at) FROM stdin;
\.


--
-- Data for Name: authentication_config; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.authentication_config (id, tenant_id, ldap_config, saml_config, oauth2_config, azure_ad_config, google_config, okta_config, mfa_config, password_policy, session_config, created_at, updated_at) FROM stdin;
1	1	{"enabled": false, "server": "", "port": 389, "use_ssl": false, "base_dn": "", "bind_dn": "", "bind_password": "", "user_filter": "(uid={username})", "group_filter": "", "admin_group": "", "user_group": "", "viewer_group": ""}	{"enabled": false, "entity_id": "", "sso_url": "", "slo_url": "", "x509_cert": "", "attribute_mapping": {"email": "email", "name": "name", "role": "role"}}	{"enabled": false, "provider": "generic", "client_id": "", "client_secret": "", "authorization_url": "", "token_url": "", "userinfo_url": "", "scope": "openid profile email", "attribute_mapping": {"email": "email", "name": "name", "role": "role"}}	{"enabled": false, "tenant_id": "", "client_id": "", "client_secret": "", "redirect_uri": "", "admin_group_id": "", "user_group_id": "", "viewer_group_id": ""}	{"enabled": false, "client_id": "", "client_secret": "", "redirect_uri": "", "hosted_domain": "", "admin_group": "", "user_group": "", "viewer_group": ""}	{"enabled": false, "domain": "", "client_id": "", "client_secret": "", "redirect_uri": "", "admin_group": "", "user_group": "", "viewer_group": ""}	{"enabled": false, "method": "totp", "issuer": "CorujaMonitor", "enforce_for_admins": true, "enforce_for_all": false}	{"min_length": 8, "require_uppercase": true, "require_lowercase": true, "require_numbers": true, "require_special": true, "expiry_days": 90, "prevent_reuse": 5}	{"timeout_minutes": 480, "max_concurrent_sessions": 3, "remember_me_days": 30}	2026-03-04 18:55:49.070609+00	2026-03-04 19:29:24.318275+00
\.


--
-- Data for Name: auto_resolution_config; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.auto_resolution_config (id, tenant_id, auto_resolution_enabled, require_approval_for_critical, min_confidence_threshold, min_success_rate_threshold, cpu_auto_resolve, cpu_max_risk_level, memory_auto_resolve, memory_max_risk_level, disk_auto_resolve, disk_max_risk_level, service_auto_resolve, service_max_risk_level, network_auto_resolve, network_max_risk_level, allowed_hours_start, allowed_hours_end, allowed_days, notify_before_execution, notify_after_execution, notification_channels, max_executions_per_hour, max_executions_per_day, cooldown_minutes, created_at, updated_at) FROM stdin;
1	1	f	t	0.8	0.85	f	low	f	low	t	medium	f	low	f	low	0	23	\N	t	t	\N	5	20	30	2026-02-25 19:14:15.831011+00	\N
\.


--
-- Data for Name: custom_reports; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.custom_reports (id, tenant_id, user_id, name, description, report_type, filters, columns, sort_by, sort_order, is_public, is_favorite, created_at, updated_at, last_generated_at) FROM stdin;
\.


--
-- Data for Name: incidents; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.incidents (id, sensor_id, severity, status, title, description, root_cause, ai_analysis, remediation_attempted, remediation_successful, created_at, resolved_at, acknowledged_at, acknowledged_by, acknowledgement_notes, resolution_notes) FROM stdin;
\.


--
-- Data for Name: knowledge_base; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.knowledge_base (id, tenant_id, problem_signature, sensor_type, severity, problem_title, problem_description, symptoms, root_cause, root_cause_confidence, solution_description, solution_steps, solution_commands, learned_from_incident_id, learned_from_user_id, times_matched, times_successful, success_rate, auto_resolution_enabled, requires_approval, risk_level, affected_os, affected_versions, prerequisites, rollback_steps, created_at, updated_at, last_matched_at) FROM stdin;
27	1	ping_timeout_network	ping	critical	Ping Falha - Rede	Problema de rede física	["Tudo inacess\\u00edvel"]	Cabo/switch/interface	0.75	Verificar física	["Verificar cabo", "Console f\\u00edsico"]	["ipconfig /all"]	\N	\N	0	0	0.65	f	t	high	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
28	1	network_port_exhaustion	network	critical	Esgotamento de Portas TCP	Portas TCP esgotadas (>65k conexões)	["Novas conex\\u00f5es falham", "TIME_WAIT alto"]	Muitas conexões não fechadas	0.88	Ajustar TcpTimedWaitDelay	["Reduzir TIME_WAIT", "Aumentar range portas"]	["netstat -ano | find /c \\"TIME_WAIT\\""]	\N	\N	0	0	0.82	f	t	medium	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
29	1	linux_disk_full_var	disk	critical	Linux - /var Cheio	/var com >90% (logs)	["/var >90%"]	Logs não rotacionados	0.9	Limpar logs antigos	["find /var/log -type f -name '*.log' -mtime +30 -delete"]	["du -sh /var/log/*", "journalctl --vacuum-time=7d"]	\N	\N	0	0	0.85	f	t	medium	["Ubuntu", "CentOS", "RHEL", "Debian"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
30	1	linux_high_load	cpu	critical	Linux - Load Average Alto	Load average >número de CPUs	["Load >CPUs", "Sistema lento"]	Processos bloqueados ou CPU alta	0.8	Identificar processos	["top", "ps aux", "Identificar processo"]	["top -b -n 1", "ps aux --sort=-%cpu | head"]	\N	\N	0	0	0.75	f	t	medium	["Ubuntu", "CentOS", "RHEL", "Debian"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
11	1	service_stopped_iis	service	critical	IIS (W3SVC) Parado	Serviço IIS parado, sites inacessíveis	["Site n\\u00e3o responde", "Erro 503"]	Serviço parado ou travou	0.95	Reiniciar IIS	["net start W3SVC"]	["net start W3SVC", "iisreset /start"]	\N	\N	0	0	0.95	t	f	low	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
12	1	service_stopped_sql	service	critical	SQL Server Parado	SQL Server parado, bancos inacessíveis	["Erro conex\\u00e3o SQL"]	Serviço parado	0.9	Reiniciar SQL	["net start MSSQLSERVER"]	["net start MSSQLSERVER"]	\N	\N	0	0	0.88	t	t	medium	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
13	1	service_stopped_spooler	service	warning	Print Spooler Parado	Spooler parado, impressão não funciona	["Impressoras n\\u00e3o funcionam"]	Trabalho corrompido	0.92	Limpar fila e reiniciar	["Limpar fila", "Reiniciar spooler"]	["net stop spooler", "del /Q /F /S C:\\\\Windows\\\\System32\\\\spool\\\\PRINTERS\\\\*", "net start spooler"]	\N	\N	0	0	0.93	t	f	low	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
14	1	service_stopped_dns	service	critical	DNS Server Parado	DNS parado, resolução de nomes falha	["DNS n\\u00e3o resolve"]	Serviço parado	0.88	Reiniciar DNS	["net start DNS"]	["net start DNS"]	\N	\N	0	0	0.9	t	f	low	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
15	1	service_stopped_dhcp	service	critical	DHCP Server Parado	DHCP parado, clientes sem IP	["Clientes n\\u00e3o obt\\u00eam IP"]	Serviço parado	0.85	Reiniciar DHCP	["net start DHCPServer"]	["net start DHCPServer"]	\N	\N	0	0	0.87	t	f	low	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
16	1	disk_full_temp	disk	critical	Disco Cheio - Arquivos Temp	Disco >90% por arquivos temporários	["Disco C: >90%"]	Acúmulo de temp	0.85	Limpar temp	["Disk Cleanup"]	["cleanmgr /sagerun:1"]	\N	\N	0	0	0.82	f	t	medium	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
17	1	disk_full_logs	disk	warning	Disco Cheio - Logs	Logs não rotacionados enchendo disco	["Logs grandes"]	Sem rotação	0.88	Rotacionar logs	["Configurar rota\\u00e7\\u00e3o"]	["forfiles /p C:\\\\inetpub\\\\logs /m *.log /d -30 /c \\"cmd /c del @path\\""]	\N	\N	0	0	0.85	f	t	medium	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
18	1	disk_full_pagefile	disk	warning	Disco Cheio - Pagefile Grande	Pagefile consumindo muito espaço	["pagefile.sys grande"]	Tamanho gerenciado	0.8	Ajustar pagefile	["Configurar tamanho fixo"]	["wmic pagefile list"]	\N	\N	0	0	0.75	f	t	medium	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
19	1	disk_full_winsxs	disk	warning	Disco Cheio - WinSxS	WinSxS >10GB	["WinSxS grande"]	Componentes antigos	0.9	Limpar componentes	["DISM cleanup"]	["Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase"]	\N	\N	0	0	0.88	f	t	low	["Windows Server 2012 R2+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
20	1	memory_leak_process	memory	critical	Memory Leak em Processo	Processo com memory leak	["Mem\\u00f3ria >95%"]	Leak de aplicação	0.8	Reiniciar processo	["Identificar e reiniciar"]	["tasklist /v", "taskkill /F"]	\N	\N	0	0	0.7	f	t	high	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
21	1	memory_high_cache	memory	warning	Memória Alta - Cache (Normal)	Cache de sistema (comportamento normal)	["Mem\\u00f3ria >80% mas responsivo"]	Cache normal Windows	0.95	Verificar se é cache	["Analisar standby memory"]	["Get-Counter '\\\\Memory\\\\Available MBytes'"]	\N	\N	0	0	0.92	f	f	low	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
22	1	memory_pool_leak	memory	critical	Pool Leak - Driver	Non-Paged Pool crescendo (driver bug)	["Pool leak", "Poss\\u00edvel BSOD"]	Driver com bug	0.75	Atualizar driver	["Identificar driver", "Atualizar"]	["poolmon.exe"]	\N	\N	0	0	0.65	f	t	high	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
23	1	cpu_high_antivirus	cpu	warning	CPU Alta - Antivírus	Scan de antivírus consumindo CPU	["CPU >90%", "MsMpEng.exe"]	Scan em horário produção	0.92	Reagendar scan	["Reagendar para noturno"]	["Set-MpPreference -ScanScheduleTime 02:00"]	\N	\N	0	0	0.88	f	t	low	["Windows Server 2016+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
24	1	cpu_high_windows_update	cpu	warning	CPU Alta - Windows Update	Windows Update instalando patches	["CPU alta", "TiWorker.exe"]	Update em produção	0.9	Aguardar conclusão	["Aguardar ou reagendar"]	["Get-WindowsUpdateLog"]	\N	\N	0	0	0.95	f	f	low	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
25	1	cpu_high_sql_query	cpu	critical	CPU Alta - Query SQL	Query SQL mal otimizada	["CPU >90%", "sqlservr.exe"]	Query sem índice	0.85	Otimizar query	["Identificar query", "Criar \\u00edndices"]	["sp_who2"]	\N	\N	0	0	0.78	f	t	medium	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
26	1	ping_timeout_firewall	ping	critical	Ping Falha - Firewall	Firewall bloqueando ICMP	["Ping timeout mas RDP ok"]	Firewall bloqueia ICMP	0.85	Permitir ICMP	["Ajustar firewall"]	["netsh advfirewall firewall add rule name=\\"ICMP\\" protocol=icmpv4:8,any dir=in action=allow"]	\N	\N	0	0	0.9	f	t	low	["Windows Server 2012+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
31	1	linux_oom_killer	memory	critical	Linux - OOM Killer Ativo	OOM Killer matando processos	["Processos morrem", "dmesg OOM"]	Memória insuficiente	0.92	Adicionar RAM ou swap	["Verificar dmesg", "Adicionar swap", "Otimizar aplica\\u00e7\\u00f5es"]	["dmesg | grep -i 'out of memory'", "free -h"]	\N	\N	0	0	0.7	f	t	high	["Ubuntu", "CentOS", "RHEL", "Debian"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
32	1	linux_service_failed	service	critical	Linux - Serviço Systemd Failed	Serviço systemd em estado failed	["systemctl status failed"]	Serviço travou ou erro config	0.85	Reiniciar serviço	["systemctl restart <service>", "journalctl -u <service>"]	["systemctl restart", "systemctl status"]	\N	\N	0	0	0.88	t	f	low	["Ubuntu 16.04+", "CentOS 7+", "RHEL 7+"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
57	1	win_firewall_blocking	network	warning	Firewall Bloqueando	Conexão bloqueada	["Conex\\u00e3o bloqueada"]	Regra firewall	0.85	Resolver Firewall Bloqueando	["Executar comandos"]	["netsh advfirewall show"]	\N	\N	0	0	0.85	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
33	1	linux_disk_io_high	disk	warning	Linux - I/O Disk Alto	I/O wait >20%	["iowait alto", "Sistema lento"]	Disco lento ou processo I/O intensivo	0.78	Identificar processo I/O	["iotop", "Identificar processo", "Otimizar ou mover para SSD"]	["iostat -x 1", "iotop -o"]	\N	\N	0	0	0.72	f	t	medium	["Ubuntu", "CentOS", "RHEL", "Debian"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
34	1	linux_ssh_too_many_auth	service	warning	Linux - SSH Too Many Auth Failures	SSH bloqueando por muitas tentativas	["SSH recusa conex\\u00e3o", "Too many authentication failures"]	Muitas chaves SSH ou tentativas	0.9	Limitar chaves ou usar IdentitiesOnly	["ssh -o IdentitiesOnly=yes", "Reduzir chaves em ~/.ssh"]	["ssh -v"]	\N	\N	0	0	0.92	f	f	low	["Ubuntu", "CentOS", "RHEL", "Debian"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
35	1	azure_vm_deallocated	ping	critical	Azure VM - Deallocated	VM Azure em estado Deallocated	["VM n\\u00e3o responde", "Portal mostra Deallocated"]	VM foi parada/deallocada	0.95	Iniciar VM via Portal/CLI	["az vm start"]	["az vm start --resource-group <rg> --name <vm>"]	\N	\N	0	0	0.98	f	t	low	["Azure"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
36	1	azure_disk_throttling	disk	warning	Azure - Disk Throttling	Disco Azure atingindo limite IOPS	["I/O lento", "Throttling metrics"]	IOPS excedido para tier do disco	0.88	Upgrade disk tier ou Premium SSD	["Verificar metrics", "Upgrade para Premium SSD"]	["az disk update --sku Premium_LRS"]	\N	\N	0	0	0.85	f	t	medium	["Azure"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
37	1	azure_nsg_blocking	network	critical	Azure - NSG Bloqueando Tráfego	Network Security Group bloqueando porta	["Conex\\u00e3o recusada", "Timeout"]	Regra NSG bloqueando	0.9	Adicionar regra NSG	["Verificar NSG", "Adicionar regra allow"]	["az network nsg rule create"]	\N	\N	0	0	0.92	f	t	medium	["Azure"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
38	1	azure_quota_exceeded	cpu	critical	Azure - Quota de vCPU Excedida	Não pode criar VM - quota excedida	["Erro ao criar VM", "QuotaExceeded"]	Limite de vCPU da subscription	0.95	Solicitar aumento de quota	["Abrir ticket suporte", "Solicitar aumento"]	["az vm list-usage --location <region>"]	\N	\N	0	0	0.88	f	t	low	["Azure"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
39	1	aks_pod_crashloopbackoff	service	critical	AKS - Pod CrashLoopBackOff	Pod reiniciando continuamente	["Pod CrashLoopBackOff", "Aplica\\u00e7\\u00e3o indispon\\u00edvel"]	Erro na aplicação ou config	0.85	Verificar logs do pod	["kubectl logs", "kubectl describe pod", "Corrigir erro"]	["kubectl logs <pod>", "kubectl describe pod <pod>"]	\N	\N	0	0	0.75	f	t	high	["AKS", "Kubernetes"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
40	1	aks_node_notready	ping	critical	AKS - Node NotReady	Node do cluster em estado NotReady	["Node NotReady", "Pods n\\u00e3o agendam"]	Kubelet parado, rede, ou recursos	0.8	Verificar node e reiniciar se necessário	["kubectl describe node", "Verificar kubelet", "Reiniciar node"]	["kubectl get nodes", "kubectl describe node <node>"]	\N	\N	0	0	0.7	f	t	high	["AKS", "Kubernetes"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
41	1	aks_imagepullbackoff	service	warning	AKS - ImagePullBackOff	Não consegue baixar imagem do container	["ImagePullBackOff", "Pod n\\u00e3o inicia"]	Imagem não existe ou sem credenciais	0.92	Verificar imagem e credenciais	["Verificar nome imagem", "Verificar imagePullSecrets", "Corrigir"]	["kubectl describe pod <pod>"]	\N	\N	0	0	0.9	f	f	low	["AKS", "Kubernetes"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
42	1	aks_pvc_pending	disk	warning	AKS - PVC Pending	PersistentVolumeClaim em estado Pending	["PVC Pending", "Pod n\\u00e3o inicia"]	StorageClass não existe ou sem quota	0.88	Verificar StorageClass e quota	["kubectl get storageclass", "Verificar quota Azure", "Corrigir"]	["kubectl get pvc", "kubectl describe pvc <pvc>"]	\N	\N	0	0	0.82	f	t	medium	["AKS", "Kubernetes"]	\N	\N	\N	2026-02-26 14:21:03.466867+00	\N	\N
43	1	win_disk_full	disk	critical	Disco C: Cheio	Disco >95%	["Disco >95%"]	Temp files	0.92	Resolver Disco C: Cheio	["Executar comandos"]	["cleanmgr /sagerun:1"]	\N	\N	0	0	0.92	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
44	1	win_mem_high	memory	warning	Memória Alta	RAM >90%	["RAM >90%"]	Memory leak	0.85	Resolver Memória Alta	["Executar comandos"]	["Get-Process | Sort WS"]	\N	\N	0	0	0.85	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
45	1	win_cpu_high	cpu	warning	CPU Alta	CPU >85%	["CPU >85%"]	Processo alto	0.8	Resolver CPU Alta	["Executar comandos"]	["Get-Process | Sort CPU"]	\N	\N	0	0	0.8	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
46	1	win_iis_stopped	service	critical	IIS Parado	W3SVC stopped	["W3SVC stopped"]	Serviço parou	0.96	Resolver IIS Parado	["Executar comandos"]	["net start W3SVC"]	\N	\N	0	0	0.96	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
47	1	win_sql_stopped	service	critical	SQL Server Parado	MSSQLSERVER stopped	["MSSQLSERVER stopped"]	Serviço parou	0.88	Resolver SQL Server Parado	["Executar comandos"]	["net start MSSQLSERVER"]	\N	\N	0	0	0.88	t	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
48	1	win_dns_stopped	service	critical	DNS Parado	DNS stopped	["DNS stopped"]	Serviço parou	0.94	Resolver DNS Parado	["Executar comandos"]	["net start DNS"]	\N	\N	0	0	0.94	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
49	1	win_dhcp_stopped	service	critical	DHCP Parado	DHCP stopped	["DHCP stopped"]	Serviço parou	0.93	Resolver DHCP Parado	["Executar comandos"]	["net start DHCPServer"]	\N	\N	0	0	0.93	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
50	1	win_ad_stopped	service	critical	Active Directory Parado	NTDS stopped	["NTDS stopped"]	Serviço parou	0.85	Resolver Active Directory Parado	["Executar comandos"]	["net start NTDS"]	\N	\N	0	0	0.85	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
51	1	win_spooler_stopped	service	warning	Print Spooler Parado	Spooler stopped	["Spooler stopped"]	Fila travada	0.93	Resolver Print Spooler Parado	["Executar comandos"]	["net stop spooler", "net start spooler"]	\N	\N	0	0	0.93	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
52	1	win_updates_pending	system	warning	Updates Pendentes	Patches aguardando	["Patches aguardando"]	Updates instalados	0.9	Resolver Updates Pendentes	["Executar comandos"]	["Get-WindowsUpdate"]	\N	\N	0	0	0.9	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
53	1	win_event_log_full	system	warning	Event Log Cheio	Logs cheios	["Logs cheios"]	Logs não rotacionados	0.88	Resolver Event Log Cheio	["Executar comandos"]	["wevtutil cl Application"]	\N	\N	0	0	0.88	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
54	1	win_time_sync_fail	system	warning	Sincronização Tempo	Time out of sync	["Time out of sync"]	NTP falhou	0.87	Resolver Sincronização Tempo	["Executar comandos"]	["w32tm /resync"]	\N	\N	0	0	0.87	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
55	1	win_cert_expired	system	critical	Certificado Expirado	SSL cert expired	["SSL cert expired"]	Cert venceu	0.95	Resolver Certificado Expirado	["Executar comandos"]	["Renovar certificado"]	\N	\N	0	0	0.95	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
56	1	win_backup_failed	system	critical	Backup Falhou	Backup error	["Backup error"]	Espaço/permissão	0.82	Resolver Backup Falhou	["Executar comandos"]	["Verificar logs"]	\N	\N	0	0	0.82	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
58	1	linux_disk_full	disk	critical	Disco Cheio Linux	Disco >95%	["Disco >95%"]	Logs grandes	0.9	Resolver Disco Cheio Linux	["Executar comandos"]	["df -h"]	\N	\N	0	0	0.9	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
59	1	linux_mem_high	memory	warning	Memória Alta Linux	RAM >90%	["RAM >90%"]	Processo alto	0.83	Resolver Memória Alta Linux	["Executar comandos"]	["free -m"]	\N	\N	0	0	0.83	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
60	1	linux_cpu_high	cpu	warning	CPU Alta Linux	CPU >85%	["CPU >85%"]	Processo alto	0.78	Resolver CPU Alta Linux	["Executar comandos"]	["top"]	\N	\N	0	0	0.78	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
61	1	linux_apache_down	service	critical	Apache Parado	httpd stopped	["httpd stopped"]	Serviço parou	0.94	Resolver Apache Parado	["Executar comandos"]	["systemctl start apache2"]	\N	\N	0	0	0.94	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
62	1	linux_nginx_down	service	critical	Nginx Parado	nginx stopped	["nginx stopped"]	Serviço parou	0.95	Resolver Nginx Parado	["Executar comandos"]	["systemctl start nginx"]	\N	\N	0	0	0.95	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
63	1	linux_mysql_down	service	critical	MySQL Parado	mysqld stopped	["mysqld stopped"]	Serviço parou	0.89	Resolver MySQL Parado	["Executar comandos"]	["systemctl start mysql"]	\N	\N	0	0	0.89	t	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
64	1	linux_ssh_down	service	critical	SSH Parado	sshd stopped	["sshd stopped"]	Serviço parou	0.92	Resolver SSH Parado	["Executar comandos"]	["systemctl start sshd"]	\N	\N	0	0	0.92	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
65	1	linux_docker_down	service	critical	Docker Parado	docker stopped	["docker stopped"]	Serviço parou	0.91	Resolver Docker Parado	["Executar comandos"]	["systemctl start docker"]	\N	\N	0	0	0.91	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
66	1	linux_ntp_unsync	system	warning	NTP Dessincronizado	Time drift	["Time drift"]	NTP falhou	0.86	Resolver NTP Dessincronizado	["Executar comandos"]	["ntpdate pool.ntp.org"]	\N	\N	0	0	0.86	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
67	1	linux_zombie_procs	system	warning	Processos Zumbis	Zombie processes	["Zombie processes"]	Processos órfãos	0.75	Resolver Processos Zumbis	["Executar comandos"]	["ps aux | grep Z"]	\N	\N	0	0	0.75	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
68	1	linux_load_high	system	warning	Load Average Alto	Load >5	["Load >5"]	Muitos processos	0.8	Resolver Load Average Alto	["Executar comandos"]	["uptime"]	\N	\N	0	0	0.8	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
69	1	linux_swap_high	memory	warning	Swap Alto	Swap >80%	["Swap >80%"]	Pouca RAM	0.82	Resolver Swap Alto	["Executar comandos"]	["free -m"]	\N	\N	0	0	0.82	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
70	1	linux_inode_full	disk	critical	Inodes Esgotados	No inodes	["No inodes"]	Muitos arquivos	0.88	Resolver Inodes Esgotados	["Executar comandos"]	["df -i"]	\N	\N	0	0	0.88	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
71	1	linux_fs_readonly	disk	critical	Filesystem Read-Only	FS remounted RO	["FS remounted RO"]	Erro disco	0.87	Resolver Filesystem Read-Only	["Executar comandos"]	["mount -o remount,rw /"]	\N	\N	0	0	0.87	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
72	1	docker_container_down	docker	critical	Container Parado	Container stopped	["Container stopped"]	Container crashed	0.92	Resolver Container Parado	["Executar comandos"]	["docker start"]	\N	\N	0	0	0.92	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
73	1	docker_high_mem	docker	warning	Container Alto Memória	Container >90% mem	["Container >90% mem"]	Memory leak	0.8	Resolver Container Alto Memória	["Executar comandos"]	["docker stats"]	\N	\N	0	0	0.8	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
74	1	docker_disk_full	docker	critical	Docker Disk Full	No space left	["No space left"]	Images/volumes	0.88	Resolver Docker Disk Full	["Executar comandos"]	["docker system prune"]	\N	\N	0	0	0.88	t	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
75	1	docker_network_issue	docker	warning	Rede Docker Problema	Network error	["Network error"]	Bridge issue	0.75	Resolver Rede Docker Problema	["Executar comandos"]	["docker network ls"]	\N	\N	0	0	0.75	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
76	1	docker_compose_down	docker	critical	Docker Compose Down	Stack down	["Stack down"]	Compose failed	0.85	Resolver Docker Compose Down	["Executar comandos"]	["docker-compose up -d"]	\N	\N	0	0	0.85	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
77	1	docker_registry_unreachable	docker	warning	Registry Inacessível	Pull failed	["Pull failed"]	Network/auth	0.82	Resolver Registry Inacessível	["Executar comandos"]	["docker login"]	\N	\N	0	0	0.82	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
78	1	docker_volume_full	docker	critical	Volume Docker Cheio	Volume full	["Volume full"]	Dados acumulados	0.86	Resolver Volume Docker Cheio	["Executar comandos"]	["docker volume ls"]	\N	\N	0	0	0.86	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
79	1	docker_daemon_down	service	critical	Docker Daemon Parado	dockerd stopped	["dockerd stopped"]	Daemon crashed	0.9	Resolver Docker Daemon Parado	["Executar comandos"]	["systemctl start docker"]	\N	\N	0	0	0.9	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
80	1	docker_swarm_node_down	docker	critical	Swarm Node Down	Node unavailable	["Node unavailable"]	Node failed	0.83	Resolver Swarm Node Down	["Executar comandos"]	["docker node ls"]	\N	\N	0	0	0.83	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
81	1	docker_healthcheck_fail	docker	warning	Healthcheck Falhando	Container unhealthy	["Container unhealthy"]	App issue	0.78	Resolver Healthcheck Falhando	["Executar comandos"]	["docker inspect"]	\N	\N	0	0	0.78	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
82	1	aks_pod_crashloop	kubernetes	critical	Pod CrashLoopBackOff	Pod restarting	["Pod restarting"]	App error	0.85	Resolver Pod CrashLoopBackOff	["Executar comandos"]	["kubectl describe pod"]	\N	\N	0	0	0.85	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
83	1	aks_hpa_not_scaling	kubernetes	warning	HPA Não Escalando	No scaling	["No scaling"]	Metrics issue	0.78	Resolver HPA Não Escalando	["Executar comandos"]	["kubectl get hpa"]	\N	\N	0	0	0.78	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
84	1	aks_ingress_down	kubernetes	critical	Ingress Controller Down	Ingress failed	["Ingress failed"]	Controller issue	0.86	Resolver Ingress Controller Down	["Executar comandos"]	["kubectl get ingress"]	\N	\N	0	0	0.86	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
85	1	azure_vm_stopped	azure	critical	VM Azure Parada	VM deallocated	["VM deallocated"]	VM stopped	0.9	Resolver VM Azure Parada	["Executar comandos"]	["az vm start"]	\N	\N	0	0	0.9	t	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
86	1	azure_sql_high_dtu	azure	warning	Azure SQL Alto DTU	DTU >90%	["DTU >90%"]	Query pesada	0.83	Resolver Azure SQL Alto DTU	["Executar comandos"]	["Verificar queries"]	\N	\N	0	0	0.83	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
87	1	azure_storage_throttle	azure	warning	Storage Throttling	Throttled requests	["Throttled requests"]	Limite atingido	0.8	Resolver Storage Throttling	["Executar comandos"]	["Aumentar tier"]	\N	\N	0	0	0.8	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
88	1	azure_app_service_down	azure	critical	App Service Down	App stopped	["App stopped"]	App crashed	0.87	Resolver App Service Down	["Executar comandos"]	["az webapp start"]	\N	\N	0	0	0.87	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
89	1	azure_function_timeout	azure	warning	Function Timeout	Execution timeout	["Execution timeout"]	Código lento	0.75	Resolver Function Timeout	["Executar comandos"]	["Otimizar c\\u00f3digo"]	\N	\N	0	0	0.75	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
90	1	ubnt_ap_offline	snmp	critical	AP Ubiquiti Offline	AP não responde	["AP n\\u00e3o responde"]	AP sem energia/rede	0.88	Resolver AP Ubiquiti Offline	["Executar comandos"]	["Verificar PoE"]	\N	\N	0	0	0.88	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
91	1	ubnt_ap_high_clients	snmp	warning	AP Muitos Clientes	Clients >50	["Clients >50"]	Sobrecarga	0.82	Resolver AP Muitos Clientes	["Executar comandos"]	["Balancear carga"]	\N	\N	0	0	0.82	f	t	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
92	1	ubnt_ap_weak_signal	snmp	warning	Sinal Fraco AP	Signal <-70dBm	["Signal <-70dBm"]	Interferência	0.75	Resolver Sinal Fraco AP	["Executar comandos"]	["Ajustar canal"]	\N	\N	0	0	0.75	f	t	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
93	1	ubnt_switch_port_down	snmp	warning	Porta Switch Down	Port down	["Port down"]	Cabo/dispositivo	0.85	Resolver Porta Switch Down	["Executar comandos"]	["Verificar cabo"]	\N	\N	0	0	0.85	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
94	1	ubnt_switch_high_errors	snmp	warning	Switch Alto Erros	CRC errors	["CRC errors"]	Cabo ruim	0.8	Resolver Switch Alto Erros	["Executar comandos"]	["Trocar cabo"]	\N	\N	0	0	0.8	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
95	1	network_high_latency	ping	warning	Latência Alta	Ping >100ms	["Ping >100ms"]	Congestionamento	0.78	Resolver Latência Alta	["Executar comandos"]	["Verificar link"]	\N	\N	0	0	0.78	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
96	1	network_packet_loss	ping	critical	Perda de Pacotes	Loss >5%	["Loss >5%"]	Link instável	0.83	Resolver Perda de Pacotes	["Executar comandos"]	["Verificar ISP"]	\N	\N	0	0	0.83	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
97	1	network_bandwidth_full	snmp	warning	Banda Saturada	Bandwidth >90%	["Bandwidth >90%"]	Tráfego alto	0.8	Resolver Banda Saturada	["Executar comandos"]	["QoS/upgrade"]	\N	\N	0	0	0.8	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
98	1	network_dns_slow	network	warning	DNS Lento	DNS >500ms	["DNS >500ms"]	DNS server issue	0.82	Resolver DNS Lento	["Executar comandos"]	["Trocar DNS"]	\N	\N	0	0	0.82	f	t	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
99	1	network_dhcp_pool_full	network	critical	Pool DHCP Esgotado	No IPs available	["No IPs available"]	Pool pequeno	0.87	Resolver Pool DHCP Esgotado	["Executar comandos"]	["Expandir pool"]	\N	\N	0	0	0.87	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
100	1	ups_on_battery	snmp	critical	Nobreak em Bateria	On battery	["On battery"]	Falta energia	0.95	Resolver Nobreak em Bateria	["Executar comandos"]	["Verificar energia"]	\N	\N	0	0	0.95	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
101	1	ups_low_battery	snmp	critical	Bateria Baixa UPS	Battery <20%	["Battery <20%"]	Bateria fraca	0.92	Resolver Bateria Baixa UPS	["Executar comandos"]	["Trocar bateria"]	\N	\N	0	0	0.92	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
102	1	ups_overload	snmp	warning	Nobreak Sobrecarregado	Load >90%	["Load >90%"]	Muitos equipamentos	0.85	Resolver Nobreak Sobrecarregado	["Executar comandos"]	["Reduzir carga"]	\N	\N	0	0	0.85	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
103	1	ups_battery_test_fail	snmp	warning	Teste Bateria Falhou	Test failed	["Test failed"]	Bateria ruim	0.88	Resolver Teste Bateria Falhou	["Executar comandos"]	["Trocar bateria"]	\N	\N	0	0	0.88	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
104	1	ups_high_temp	snmp	warning	Temperatura Alta UPS	Temp >40C	["Temp >40C"]	Ventilação ruim	0.8	Resolver Temperatura Alta UPS	["Executar comandos"]	["Melhorar ventila\\u00e7\\u00e3o"]	\N	\N	0	0	0.8	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
105	1	ac_high_temp	snmp	critical	Temperatura Alta Sala	Temp >28C	["Temp >28C"]	AC não resfria	0.9	Resolver Temperatura Alta Sala	["Executar comandos"]	["Verificar AC"]	\N	\N	0	0	0.9	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
106	1	ac_unit_offline	snmp	critical	AC Offline	AC não responde	["AC n\\u00e3o responde"]	AC desligado	0.92	Resolver AC Offline	["Executar comandos"]	["Ligar AC"]	\N	\N	0	0	0.92	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
107	1	ac_filter_dirty	snmp	warning	Filtro AC Sujo	Airflow baixo	["Airflow baixo"]	Filtro entupido	0.85	Resolver Filtro AC Sujo	["Executar comandos"]	["Limpar filtro"]	\N	\N	0	0	0.85	f	t	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
108	1	ac_compressor_fail	snmp	critical	Compressor AC Falhou	No cooling	["No cooling"]	Compressor quebrado	0.88	Resolver Compressor AC Falhou	["Executar comandos"]	["Chamar t\\u00e9cnico"]	\N	\N	0	0	0.88	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
109	1	ac_humidity_high	snmp	warning	Umidade Alta	Humidity >70%	["Humidity >70%"]	AC não desumidifica	0.8	Resolver Umidade Alta	["Executar comandos"]	["Verificar AC"]	\N	\N	0	0	0.8	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
110	1	webapp_http_500	http	critical	Erro 500 Aplicação	HTTP 500	["HTTP 500"]	App error	0.85	Resolver Erro 500 Aplicação	["Executar comandos"]	["Verificar logs"]	\N	\N	0	0	0.85	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
111	1	webapp_http_503	http	critical	Serviço Indisponível	HTTP 503	["HTTP 503"]	App down	0.9	Resolver Serviço Indisponível	["Executar comandos"]	["Reiniciar app"]	\N	\N	0	0	0.9	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
112	1	webapp_slow_response	http	warning	Resposta Lenta	Response >3s	["Response >3s"]	Query lenta	0.78	Resolver Resposta Lenta	["Executar comandos"]	["Otimizar queries"]	\N	\N	0	0	0.78	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
113	1	webapp_ssl_expired	http	critical	Certificado SSL Expirado	SSL expired	["SSL expired"]	Cert venceu	0.95	Resolver Certificado SSL Expirado	["Executar comandos"]	["Renovar SSL"]	\N	\N	0	0	0.95	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
114	1	webapp_high_error_rate	http	warning	Taxa Erro Alta	Errors >5%	["Errors >5%"]	Bug na app	0.8	Resolver Taxa Erro Alta	["Executar comandos"]	["Verificar logs"]	\N	\N	0	0	0.8	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
115	1	webapp_db_connection_fail	http	critical	Conexão DB Falhou	DB error	["DB error"]	DB down/creds	0.88	Resolver Conexão DB Falhou	["Executar comandos"]	["Verificar DB"]	\N	\N	0	0	0.88	f	t	high	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
116	1	webapp_session_timeout	http	warning	Timeout Sessão	Session expired	["Session expired"]	Config timeout	0.75	Resolver Timeout Sessão	["Executar comandos"]	["Ajustar timeout"]	\N	\N	0	0	0.75	f	t	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
117	1	webapp_memory_leak	http	warning	Memory Leak App	Memory growing	["Memory growing"]	Leak no código	0.82	Resolver Memory Leak App	["Executar comandos"]	["Reiniciar app"]	\N	\N	0	0	0.82	t	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
118	1	webapp_cache_full	http	warning	Cache Cheio	Cache full	["Cache full"]	Cache não limpa	0.85	Resolver Cache Cheio	["Executar comandos"]	["Limpar cache"]	\N	\N	0	0	0.85	t	f	low	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
119	1	webapp_api_rate_limit	http	warning	Rate Limit Atingido	429 Too Many	["429 Too Many"]	Muitas requests	0.83	Resolver Rate Limit Atingido	["Executar comandos"]	["Aumentar limite"]	\N	\N	0	0	0.83	f	t	medium	["Multi-platform"]	\N	\N	\N	2026-02-26 18:15:33.617514+00	\N	\N
120	7	win_disk_full	disk	critical	Disco C: Cheio	Disco sistema >95%	["Disco sistema >95%"]	Temp files	0.92	Resolver Disco C: Cheio	["Executar comandos"]	["cleanmgr /sagerun:1"]	\N	\N	0	0	0.92	t	f	low	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
121	7	win_mem_high	memory	warning	Memória Alta	RAM >90%	["RAM >90%"]	Memory leak	0.85	Resolver Memória Alta	["Executar comandos"]	["Get-Process | Sort WS"]	\N	\N	0	0	0.85	f	t	medium	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
122	7	win_cpu_high	cpu	warning	CPU Alta	CPU >85%	["CPU >85%"]	Processo alto	0.8	Resolver CPU Alta	["Executar comandos"]	["Get-Process | Sort CPU"]	\N	\N	0	0	0.8	f	t	medium	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
123	7	win_iis_stopped	service	critical	IIS Parado	W3SVC stopped	["W3SVC stopped"]	Serviço parou	0.96	Resolver IIS Parado	["Executar comandos"]	["net start W3SVC"]	\N	\N	0	0	0.96	t	f	low	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
124	7	win_sql_stopped	service	critical	SQL Server Parado	MSSQLSERVER stopped	["MSSQLSERVER stopped"]	Serviço parou	0.88	Resolver SQL Server Parado	["Executar comandos"]	["net start MSSQLSERVER"]	\N	\N	0	0	0.88	t	t	medium	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
125	7	win_dns_stopped	service	critical	DNS Parado	DNS stopped	["DNS stopped"]	Serviço parou	0.94	Resolver DNS Parado	["Executar comandos"]	["net start DNS"]	\N	\N	0	0	0.94	t	f	low	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
126	7	win_dhcp_stopped	service	critical	DHCP Parado	DHCP stopped	["DHCP stopped"]	Serviço parou	0.93	Resolver DHCP Parado	["Executar comandos"]	["net start DHCPServer"]	\N	\N	0	0	0.93	t	f	low	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
127	7	win_ad_stopped	service	critical	Active Directory Parado	NTDS stopped	["NTDS stopped"]	Serviço parou	0.85	Resolver Active Directory Parado	["Executar comandos"]	["net start NTDS"]	\N	\N	0	0	0.85	f	t	high	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
128	7	win_spooler_stopped	service	warning	Print Spooler Parado	Spooler stopped	["Spooler stopped"]	Fila travada	0.93	Resolver Print Spooler Parado	["Executar comandos"]	["net stop spooler", "net start spooler"]	\N	\N	0	0	0.93	t	f	low	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
129	7	win_updates_pending	system	warning	Updates Pendentes	Patches aguardando	["Patches aguardando"]	Updates instalados	0.9	Resolver Updates Pendentes	["Executar comandos"]	["Get-WindowsUpdate"]	\N	\N	0	0	0.9	f	t	medium	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
130	7	win_event_log_full	system	warning	Event Log Cheio	Logs cheios	["Logs cheios"]	Logs não rotacionados	0.88	Resolver Event Log Cheio	["Executar comandos"]	["wevtutil cl Application"]	\N	\N	0	0	0.88	t	f	low	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
131	7	win_time_sync_fail	system	warning	Sincronização Tempo Falhou	Time out of sync	["Time out of sync"]	NTP falhou	0.87	Resolver Sincronização Tempo Falhou	["Executar comandos"]	["w32tm /resync"]	\N	\N	0	0	0.87	t	f	low	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
132	7	win_cert_expired	system	critical	Certificado Expirado	SSL cert expired	["SSL cert expired"]	Certificado venceu	0.95	Resolver Certificado Expirado	["Executar comandos"]	["Renovar certificado"]	\N	\N	0	0	0.95	f	t	high	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
133	7	win_backup_failed	system	critical	Backup Falhou	Backup error	["Backup error"]	Espaço ou permissão	0.82	Resolver Backup Falhou	["Executar comandos"]	["Verificar logs backup"]	\N	\N	0	0	0.82	f	t	high	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
134	7	win_firewall_blocking	network	warning	Firewall Bloqueando	Conexão bloqueada	["Conex\\u00e3o bloqueada"]	Regra firewall	0.85	Resolver Firewall Bloqueando	["Executar comandos"]	["netsh advfirewall show"]	\N	\N	0	0	0.85	f	t	medium	["Windows Server"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
135	7	linux_disk_full	disk	critical	Disco Cheio Linux	Disco >95%	["Disco >95%"]	Logs grandes	0.9	Resolver Disco Cheio Linux	["Executar comandos"]	["df -h", "du -sh /*"]	\N	\N	0	0	0.9	f	t	medium	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
136	7	linux_mem_high	memory	warning	Memória Alta Linux	RAM >90%	["RAM >90%"]	Processo alto	0.83	Resolver Memória Alta Linux	["Executar comandos"]	["free -m", "top"]	\N	\N	0	0	0.83	f	t	medium	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
137	7	linux_cpu_high	cpu	warning	CPU Alta Linux	CPU >85%	["CPU >85%"]	Processo alto	0.78	Resolver CPU Alta Linux	["Executar comandos"]	["top", "ps aux"]	\N	\N	0	0	0.78	f	t	medium	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
138	7	linux_apache_down	service	critical	Apache Parado	httpd stopped	["httpd stopped"]	Serviço parou	0.94	Resolver Apache Parado	["Executar comandos"]	["systemctl start apache2"]	\N	\N	0	0	0.94	t	f	low	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
139	7	linux_nginx_down	service	critical	Nginx Parado	nginx stopped	["nginx stopped"]	Serviço parou	0.95	Resolver Nginx Parado	["Executar comandos"]	["systemctl start nginx"]	\N	\N	0	0	0.95	t	f	low	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
140	7	linux_mysql_down	service	critical	MySQL Parado	mysqld stopped	["mysqld stopped"]	Serviço parou	0.89	Resolver MySQL Parado	["Executar comandos"]	["systemctl start mysql"]	\N	\N	0	0	0.89	t	t	medium	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
141	7	linux_ssh_down	service	critical	SSH Parado	sshd stopped	["sshd stopped"]	Serviço parou	0.92	Resolver SSH Parado	["Executar comandos"]	["systemctl start sshd"]	\N	\N	0	0	0.92	t	f	low	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
142	7	linux_docker_down	service	critical	Docker Parado	docker stopped	["docker stopped"]	Serviço parou	0.91	Resolver Docker Parado	["Executar comandos"]	["systemctl start docker"]	\N	\N	0	0	0.91	t	f	low	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
143	7	linux_ntp_unsync	system	warning	NTP Dessincronizado	Time drift	["Time drift"]	NTP falhou	0.86	Resolver NTP Dessincronizado	["Executar comandos"]	["ntpdate -u pool.ntp.org"]	\N	\N	0	0	0.86	t	f	low	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
144	7	linux_zombie_procs	system	warning	Processos Zumbis	Zombie processes	["Zombie processes"]	Processos órfãos	0.75	Resolver Processos Zumbis	["Executar comandos"]	["ps aux | grep Z"]	\N	\N	0	0	0.75	f	t	medium	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
145	7	linux_load_high	system	warning	Load Average Alto	Load >5	["Load >5"]	Muitos processos	0.8	Resolver Load Average Alto	["Executar comandos"]	["uptime", "top"]	\N	\N	0	0	0.8	f	t	medium	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
146	7	linux_swap_high	memory	warning	Swap Alto	Swap >80%	["Swap >80%"]	Pouca RAM	0.82	Resolver Swap Alto	["Executar comandos"]	["free -m", "swapon -s"]	\N	\N	0	0	0.82	f	t	medium	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
147	7	linux_inode_full	disk	critical	Inodes Esgotados	No inodes	["No inodes"]	Muitos arquivos	0.88	Resolver Inodes Esgotados	["Executar comandos"]	["df -i"]	\N	\N	0	0	0.88	f	t	high	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
148	7	linux_oom_killer	memory	critical	OOM Killer Ativo	Out of memory	["Out of memory"]	RAM esgotada	0.85	Resolver OOM Killer Ativo	["Executar comandos"]	["dmesg | grep oom"]	\N	\N	0	0	0.85	f	t	high	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
149	7	linux_fs_readonly	disk	critical	Filesystem Read-Only	FS remounted RO	["FS remounted RO"]	Erro disco	0.87	Resolver Filesystem Read-Only	["Executar comandos"]	["mount -o remount,rw /"]	\N	\N	0	0	0.87	f	t	high	["Linux"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
150	7	docker_container_down	docker	critical	Container Parado	Container stopped	["Container stopped"]	Container crashed	0.92	Resolver Container Parado	["Executar comandos"]	["docker start <container>"]	\N	\N	0	0	0.92	t	f	low	["Linux", "Windows"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
151	7	docker_high_mem	docker	warning	Container Alto Memória	Container >90% mem	["Container >90% mem"]	Memory leak	0.8	Resolver Container Alto Memória	["Executar comandos"]	["docker stats"]	\N	\N	0	0	0.8	f	t	medium	["Linux", "Windows"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
152	7	docker_disk_full	docker	critical	Docker Disk Full	No space left	["No space left"]	Images/volumes	0.88	Resolver Docker Disk Full	["Executar comandos"]	["docker system prune"]	\N	\N	0	0	0.88	t	t	medium	["Linux", "Windows"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
153	7	docker_network_issue	docker	warning	Rede Docker Problema	Network error	["Network error"]	Bridge issue	0.75	Resolver Rede Docker Problema	["Executar comandos"]	["docker network ls"]	\N	\N	0	0	0.75	f	t	medium	["Linux", "Windows"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
154	7	docker_compose_down	docker	critical	Docker Compose Down	Stack down	["Stack down"]	Compose failed	0.85	Resolver Docker Compose Down	["Executar comandos"]	["docker-compose up -d"]	\N	\N	0	0	0.85	t	f	low	["Linux", "Windows"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
155	7	docker_registry_unreachable	docker	warning	Registry Inacessível	Pull failed	["Pull failed"]	Network/auth	0.82	Resolver Registry Inacessível	["Executar comandos"]	["docker login"]	\N	\N	0	0	0.82	f	t	medium	["Linux", "Windows"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
156	7	docker_volume_full	docker	critical	Volume Docker Cheio	Volume full	["Volume full"]	Dados acumulados	0.86	Resolver Volume Docker Cheio	["Executar comandos"]	["docker volume ls"]	\N	\N	0	0	0.86	f	t	high	["Linux", "Windows"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
157	7	docker_daemon_down	service	critical	Docker Daemon Parado	dockerd stopped	["dockerd stopped"]	Daemon crashed	0.9	Resolver Docker Daemon Parado	["Executar comandos"]	["systemctl start docker"]	\N	\N	0	0	0.9	t	f	low	["Linux", "Windows"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
158	7	docker_swarm_node_down	docker	critical	Swarm Node Down	Node unavailable	["Node unavailable"]	Node failed	0.83	Resolver Swarm Node Down	["Executar comandos"]	["docker node ls"]	\N	\N	0	0	0.83	f	t	high	["Linux", "Windows"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
159	7	docker_healthcheck_fail	docker	warning	Healthcheck Falhando	Container unhealthy	["Container unhealthy"]	App issue	0.78	Resolver Healthcheck Falhando	["Executar comandos"]	["docker inspect"]	\N	\N	0	0	0.78	f	t	medium	["Linux", "Windows"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
160	7	aks_pod_crashloop	kubernetes	critical	Pod CrashLoopBackOff	Pod restarting	["Pod restarting"]	App error	0.85	Resolver Pod CrashLoopBackOff	["Executar comandos"]	["kubectl describe pod"]	\N	\N	0	0	0.85	f	t	high	["Azure"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
161	7	aks_node_notready	kubernetes	critical	Node NotReady	Node down	["Node down"]	Node issue	0.88	Resolver Node NotReady	["Executar comandos"]	["kubectl get nodes"]	\N	\N	0	0	0.88	f	t	high	["Azure"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
162	7	aks_pvc_pending	kubernetes	warning	PVC Pending	Volume pending	["Volume pending"]	Storage issue	0.82	Resolver PVC Pending	["Executar comandos"]	["kubectl get pvc"]	\N	\N	0	0	0.82	f	t	medium	["Azure"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
163	7	aks_hpa_not_scaling	kubernetes	warning	HPA Não Escalando	No scaling	["No scaling"]	Metrics issue	0.78	Resolver HPA Não Escalando	["Executar comandos"]	["kubectl get hpa"]	\N	\N	0	0	0.78	f	t	medium	["Azure"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
164	7	aks_ingress_down	kubernetes	critical	Ingress Controller Down	Ingress failed	["Ingress failed"]	Controller issue	0.86	Resolver Ingress Controller Down	["Executar comandos"]	["kubectl get ingress"]	\N	\N	0	0	0.86	f	t	high	["Azure"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
165	7	azure_vm_stopped	azure	critical	VM Azure Parada	VM deallocated	["VM deallocated"]	VM stopped	0.9	Resolver VM Azure Parada	["Executar comandos"]	["az vm start"]	\N	\N	0	0	0.9	t	t	medium	["Azure"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
166	7	azure_sql_high_dtu	azure	warning	Azure SQL Alto DTU	DTU >90%	["DTU >90%"]	Query pesada	0.83	Resolver Azure SQL Alto DTU	["Executar comandos"]	["Verificar queries"]	\N	\N	0	0	0.83	f	t	medium	["Azure"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
167	7	azure_storage_throttle	azure	warning	Storage Throttling	Throttled requests	["Throttled requests"]	Limite atingido	0.8	Resolver Storage Throttling	["Executar comandos"]	["Aumentar tier"]	\N	\N	0	0	0.8	f	t	medium	["Azure"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
168	7	azure_app_service_down	azure	critical	App Service Down	App stopped	["App stopped"]	App crashed	0.87	Resolver App Service Down	["Executar comandos"]	["az webapp start"]	\N	\N	0	0	0.87	t	f	low	["Azure"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
169	7	azure_function_timeout	azure	warning	Function Timeout	Execution timeout	["Execution timeout"]	Código lento	0.75	Resolver Function Timeout	["Executar comandos"]	["Otimizar c\\u00f3digo"]	\N	\N	0	0	0.75	f	t	medium	["Azure"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
170	7	ubnt_ap_offline	snmp	critical	AP Ubiquiti Offline	AP não responde	["AP n\\u00e3o responde"]	AP sem energia/rede	0.88	Resolver AP Ubiquiti Offline	["Executar comandos"]	["Verificar PoE"]	\N	\N	0	0	0.88	f	t	medium	["Network"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
171	7	ubnt_ap_high_clients	snmp	warning	AP Muitos Clientes	Clients >50	["Clients >50"]	Sobrecarga	0.82	Resolver AP Muitos Clientes	["Executar comandos"]	["Balancear carga"]	\N	\N	0	0	0.82	f	t	low	["Network"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
172	7	ubnt_ap_weak_signal	snmp	warning	Sinal Fraco AP	Signal <-70dBm	["Signal <-70dBm"]	Interferência	0.75	Resolver Sinal Fraco AP	["Executar comandos"]	["Ajustar canal"]	\N	\N	0	0	0.75	f	t	low	["Network"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
173	7	ubnt_switch_port_down	snmp	warning	Porta Switch Down	Port down	["Port down"]	Cabo/dispositivo	0.85	Resolver Porta Switch Down	["Executar comandos"]	["Verificar cabo"]	\N	\N	0	0	0.85	f	t	medium	["Network"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
174	7	ubnt_switch_high_errors	snmp	warning	Switch Alto Erros	CRC errors	["CRC errors"]	Cabo ruim	0.8	Resolver Switch Alto Erros	["Executar comandos"]	["Trocar cabo"]	\N	\N	0	0	0.8	f	t	medium	["Network"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
175	7	network_high_latency	ping	warning	Latência Alta	Ping >100ms	["Ping >100ms"]	Congestionamento	0.78	Resolver Latência Alta	["Executar comandos"]	["Verificar link"]	\N	\N	0	0	0.78	f	t	medium	["Network"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
176	7	network_packet_loss	ping	critical	Perda de Pacotes	Loss >5%	["Loss >5%"]	Link instável	0.83	Resolver Perda de Pacotes	["Executar comandos"]	["Verificar ISP"]	\N	\N	0	0	0.83	f	t	high	["Network"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
177	7	network_bandwidth_full	snmp	warning	Banda Saturada	Bandwidth >90%	["Bandwidth >90%"]	Tráfego alto	0.8	Resolver Banda Saturada	["Executar comandos"]	["QoS/upgrade"]	\N	\N	0	0	0.8	f	t	medium	["Network"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
178	7	network_dns_slow	network	warning	DNS Lento	DNS >500ms	["DNS >500ms"]	DNS server issue	0.82	Resolver DNS Lento	["Executar comandos"]	["Trocar DNS"]	\N	\N	0	0	0.82	f	t	low	["Network"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
179	7	network_dhcp_pool_full	network	critical	Pool DHCP Esgotado	No IPs available	["No IPs available"]	Pool pequeno	0.87	Resolver Pool DHCP Esgotado	["Executar comandos"]	["Expandir pool"]	\N	\N	0	0	0.87	f	t	high	["Network"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
180	7	ups_on_battery	snmp	critical	Nobreak em Bateria	On battery	["On battery"]	Falta energia	0.95	Resolver Nobreak em Bateria	["Executar comandos"]	["Verificar energia"]	\N	\N	0	0	0.95	f	t	high	["UPS"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
181	7	ups_low_battery	snmp	critical	Bateria Baixa UPS	Battery <20%	["Battery <20%"]	Bateria fraca	0.92	Resolver Bateria Baixa UPS	["Executar comandos"]	["Trocar bateria"]	\N	\N	0	0	0.92	f	t	high	["UPS"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
182	7	ups_overload	snmp	warning	Nobreak Sobrecarregado	Load >90%	["Load >90%"]	Muitos equipamentos	0.85	Resolver Nobreak Sobrecarregado	["Executar comandos"]	["Reduzir carga"]	\N	\N	0	0	0.85	f	t	medium	["UPS"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
183	7	ups_battery_test_fail	snmp	warning	Teste Bateria Falhou	Test failed	["Test failed"]	Bateria ruim	0.88	Resolver Teste Bateria Falhou	["Executar comandos"]	["Trocar bateria"]	\N	\N	0	0	0.88	f	t	high	["UPS"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
184	7	ups_high_temp	snmp	warning	Temperatura Alta UPS	Temp >40C	["Temp >40C"]	Ventilação ruim	0.8	Resolver Temperatura Alta UPS	["Executar comandos"]	["Melhorar ventila\\u00e7\\u00e3o"]	\N	\N	0	0	0.8	f	t	medium	["UPS"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
185	7	ac_high_temp	snmp	critical	Temperatura Alta Sala	Temp >28C	["Temp >28C"]	AC não resfria	0.9	Resolver Temperatura Alta Sala	["Executar comandos"]	["Verificar AC"]	\N	\N	0	0	0.9	f	t	high	["HVAC"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
186	7	ac_unit_offline	snmp	critical	AC Offline	AC não responde	["AC n\\u00e3o responde"]	AC desligado	0.92	Resolver AC Offline	["Executar comandos"]	["Ligar AC"]	\N	\N	0	0	0.92	f	t	high	["HVAC"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
187	7	ac_filter_dirty	snmp	warning	Filtro AC Sujo	Airflow baixo	["Airflow baixo"]	Filtro entupido	0.85	Resolver Filtro AC Sujo	["Executar comandos"]	["Limpar filtro"]	\N	\N	0	0	0.85	f	t	low	["HVAC"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
188	7	ac_compressor_fail	snmp	critical	Compressor AC Falhou	No cooling	["No cooling"]	Compressor quebrado	0.88	Resolver Compressor AC Falhou	["Executar comandos"]	["Chamar t\\u00e9cnico"]	\N	\N	0	0	0.88	f	t	high	["HVAC"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
189	7	ac_humidity_high	snmp	warning	Umidade Alta	Humidity >70%	["Humidity >70%"]	AC não desumidifica	0.8	Resolver Umidade Alta	["Executar comandos"]	["Verificar AC"]	\N	\N	0	0	0.8	f	t	medium	["HVAC"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
190	7	webapp_http_500	http	critical	Erro 500 Aplicação	HTTP 500	["HTTP 500"]	App error	0.85	Resolver Erro 500 Aplicação	["Executar comandos"]	["Verificar logs"]	\N	\N	0	0	0.85	f	t	high	["Web"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
191	7	webapp_http_503	http	critical	Serviço Indisponível	HTTP 503	["HTTP 503"]	App down	0.9	Resolver Serviço Indisponível	["Executar comandos"]	["Reiniciar app"]	\N	\N	0	0	0.9	t	f	low	["Web"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
192	7	webapp_slow_response	http	warning	Resposta Lenta	Response >3s	["Response >3s"]	Query lenta	0.78	Resolver Resposta Lenta	["Executar comandos"]	["Otimizar queries"]	\N	\N	0	0	0.78	f	t	medium	["Web"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
193	7	webapp_ssl_expired	http	critical	Certificado SSL Expirado	SSL expired	["SSL expired"]	Cert venceu	0.95	Resolver Certificado SSL Expirado	["Executar comandos"]	["Renovar SSL"]	\N	\N	0	0	0.95	f	t	high	["Web"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
194	7	webapp_high_error_rate	http	warning	Taxa Erro Alta	Errors >5%	["Errors >5%"]	Bug na app	0.8	Resolver Taxa Erro Alta	["Executar comandos"]	["Verificar logs"]	\N	\N	0	0	0.8	f	t	medium	["Web"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
195	7	webapp_db_connection_fail	http	critical	Conexão DB Falhou	DB error	["DB error"]	DB down/creds	0.88	Resolver Conexão DB Falhou	["Executar comandos"]	["Verificar DB"]	\N	\N	0	0	0.88	f	t	high	["Web"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
196	7	webapp_session_timeout	http	warning	Timeout Sessão	Session expired	["Session expired"]	Config timeout	0.75	Resolver Timeout Sessão	["Executar comandos"]	["Ajustar timeout"]	\N	\N	0	0	0.75	f	t	low	["Web"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
197	7	webapp_memory_leak	http	warning	Memory Leak App	Memory growing	["Memory growing"]	Leak no código	0.82	Resolver Memory Leak App	["Executar comandos"]	["Reiniciar app"]	\N	\N	0	0	0.82	t	t	medium	["Web"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
198	7	webapp_cache_full	http	warning	Cache Cheio	Cache full	["Cache full"]	Cache não limpa	0.85	Resolver Cache Cheio	["Executar comandos"]	["Limpar cache"]	\N	\N	0	0	0.85	t	f	low	["Web"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
199	7	webapp_api_rate_limit	http	warning	Rate Limit Atingido	429 Too Many	["429 Too Many"]	Muitas requests	0.83	Resolver Rate Limit Atingido	["Executar comandos"]	["Aumentar limite"]	\N	\N	0	0	0.83	f	t	medium	["Web"]	\N	\N	\N	2026-02-26 21:34:00.538441+00	\N	\N
\.


--
-- Data for Name: kubernetes_alert_rules; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.kubernetes_alert_rules (id, cluster_id, tenant_id, name, description, alert_type, severity, resource_type, metric_name, operator, threshold, duration, namespace_filter, label_filter, is_active, notify_email, notify_webhook, webhook_url, created_at, updated_at) FROM stdin;
1	\N	1	Node NotReady	Alerta quando um node fica NotReady	node_not_ready	critical	node	ready	eq	0	300	\N	{}	t	t	f	\N	2026-02-27 17:19:33.689168	2026-02-27 17:19:33.689168
2	\N	1	High CPU Usage (Node)	Alerta quando CPU do node > 90%	high_cpu	warning	node	node_cpu_usage	gt	90	300	\N	{}	t	t	f	\N	2026-02-27 17:19:33.701935	2026-02-27 17:19:33.701935
3	\N	1	High Memory Usage (Node)	Alerta quando memória do node > 90%	high_memory	warning	node	node_memory_usage	gt	90	300	\N	{}	t	t	f	\N	2026-02-27 17:19:33.704535	2026-02-27 17:19:33.704535
4	\N	1	Pod CrashLoopBackOff	Alerta quando pod tem muitos restarts	pod_crashloop	critical	pod	pod_restart_count	gt	5	600	\N	{}	t	t	f	\N	2026-02-27 17:19:33.706966	2026-02-27 17:19:33.706966
5	\N	1	Deployment Unhealthy	Alerta quando deployment não tem réplicas prontas	deployment_unhealthy	warning	deployment	ready_replicas	lt	1	300	\N	{}	t	t	f	\N	2026-02-27 17:19:33.708703	2026-02-27 17:19:33.708703
\.


--
-- Data for Name: kubernetes_alerts; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.kubernetes_alerts (id, cluster_id, resource_id, alert_type, severity, title, message, resource_type, resource_name, namespace, current_value, threshold_value, status, acknowledged_at, acknowledged_by, resolved_at, alert_metadata, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: kubernetes_clusters; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.kubernetes_clusters (id, tenant_id, probe_id, cluster_name, cluster_type, api_endpoint, auth_method, kubeconfig_content, service_account_token, ca_cert, monitor_all_namespaces, namespaces, selected_resources, collection_interval, is_active, last_connection_test, connection_status, connection_error, total_nodes, total_pods, total_deployments, cluster_cpu_usage, cluster_memory_usage, created_at, updated_at, last_collected_at) FROM stdin;
\.


--
-- Data for Name: kubernetes_metrics; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.kubernetes_metrics (id, resource_id, cpu_usage, memory_usage, network_rx_bytes, network_tx_bytes, disk_usage, status, ready, restart_count, "timestamp") FROM stdin;
\.


--
-- Data for Name: kubernetes_resources; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.kubernetes_resources (id, cluster_id, resource_type, resource_name, namespace, uid, labels, annotations, status, phase, ready, metrics, node_cpu_capacity, node_memory_capacity, node_cpu_usage, node_memory_usage, node_pod_count, node_pod_capacity, pod_cpu_usage, pod_memory_usage, pod_restart_count, pod_node_name, desired_replicas, ready_replicas, available_replicas, updated_replicas, created_at, updated_at, last_seen_at) FROM stdin;
\.


--
-- Data for Name: learning_sessions; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.learning_sessions (id, tenant_id, incident_id, user_id, problem_description, root_cause_identified, solution_applied, resolution_steps, commands_used, sensor_type, severity, resolution_time_minutes, added_to_knowledge_base, knowledge_base_id, confidence_score, was_successful, technician_notes, created_at, learned_at) FROM stdin;
\.


--
-- Data for Name: maintenance_windows; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.maintenance_windows (id, tenant_id, server_id, title, description, start_time, end_time, created_by, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: metrics; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.metrics (id, sensor_id, value, unit, status, "timestamp", metadata) FROM stdin;
\.


--
-- Data for Name: monthly_reports; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.monthly_reports (id, tenant_id, year, month, availability_percentage, total_incidents, auto_resolved_incidents, sla_compliance, report_data, ai_summary, generated_at) FROM stdin;
\.


--
-- Data for Name: probes; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.probes (id, tenant_id, name, token, is_active, last_heartbeat, version, created_at) FROM stdin;
\.


--
-- Data for Name: remediation_logs; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.remediation_logs (id, incident_id, action_type, action_description, before_state, after_state, success, error_message, executed_at) FROM stdin;
\.


--
-- Data for Name: resolution_attempts; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.resolution_attempts (id, tenant_id, incident_id, knowledge_base_id, problem_signature, solution_applied, commands_executed, status, success, error_message, execution_time_seconds, state_before, state_after, requires_approval, approved_by, approved_at, approval_notes, technician_feedback, feedback_rating, feedback_by, feedback_at, created_at, executed_at, completed_at) FROM stdin;
\.


--
-- Data for Name: sensor_breach_history; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.sensor_breach_history (id, sensor_id, breach_start, breach_end, breach_value, threshold_type, incident_created, incident_id, created_at) FROM stdin;
\.


--
-- Data for Name: sensor_groups; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.sensor_groups (id, tenant_id, name, parent_id, description, icon, color, created_at, updated_at) FROM stdin;
1	7	Sensores Não Agrupados	\N	Sensores sem grupo definido	📦	#999999	2026-02-27 12:41:36.16949	2026-02-27 12:41:36.16949
\.


--
-- Data for Name: sensor_notes; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.sensor_notes (id, sensor_id, user_id, note, status, created_at) FROM stdin;
\.


--
-- Data for Name: sensors; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.sensors (id, server_id, name, sensor_type, config, threshold_warning, threshold_critical, is_active, created_at, verification_status, last_note, last_note_by, last_note_at, collection_protocol, snmp_oid, is_acknowledged, acknowledged_by, acknowledged_at, probe_id, group_id) FROM stdin;
\.


--
-- Data for Name: servers; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.servers (id, tenant_id, probe_id, hostname, ip_address, os_type, os_version, is_active, created_at, public_ip, group_name, tags, device_type, monitoring_protocol, snmp_version, snmp_community, snmp_port, environment, monitoring_schedule, wmi_username, wmi_password_encrypted, wmi_domain, wmi_enabled, updated_at) FROM stdin;
\.


--
-- Data for Name: tenants; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.tenants (id, name, slug, is_active, created_at, updated_at, notification_config) FROM stdin;
1	Default	default	t	2026-02-11 17:42:50.924435+00	2026-02-25 19:20:59.721521+00	{"email": {"enabled": false, "smtp_server": "", "smtp_port": 587, "smtp_user": "", "smtp_password": "", "from_email": "", "to_emails": [], "use_tls": true}, "twilio": {"enabled": false, "account_sid": "", "auth_token": "", "from_number": "", "to_numbers": []}, "teams": {"enabled": false, "webhook_url": "https://techbizfd.webhook.office.com/webhookb2/1fce8d39-1753-47cd-8927-c2b01053abfe@6731fa33-e076-4815-8003-ad91af58421f/IncomingWebhook/c14a5355d3054a9ea9d84fae987f7f7b/beb27b50-822b-4170-81d2-7d3f2d7c52ca/V2qbpey1Z3wmlFi7FELnO3EoWx7tGUAB1dq-dpFcpG70I1"}, "whatsapp": {"enabled": false, "api_key": "", "phone_numbers": []}, "telegram": {"enabled": false, "bot_token": "", "chat_ids": []}, "topdesk": {"enabled": false, "url": "https://grupotechbiz.topdesk.net", "username": "coruja.monitor", "password": "ijsnz-cluur-lsr7i-lka62-3lwwp", "operator_group": "Analista de Infraestrutura", "category": "Suporte T\\u00e9cnico Infraestrutura", "subcategory": "Outro"}, "glpi": {"enabled": false, "url": "", "app_token": "", "user_token": "", "entity_id": "", "category_id": "", "urgency": 4, "impact": 3}}
7	Techbiz	techbiz	f	2026-02-24 13:13:26.174219+00	2026-03-05 14:46:47.180295+00	\N
\.


--
-- Data for Name: threshold_config; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.threshold_config (id, tenant_id, breach_duration_seconds, flapping_window_seconds, flapping_threshold, cpu_breach_duration, memory_breach_duration, disk_breach_duration, ping_breach_duration, service_breach_duration, network_breach_duration, suppress_during_maintenance, suppress_acknowledged, suppress_flapping, escalation_enabled, escalation_time_minutes, escalation_severity, created_at, updated_at) FROM stdin;
1	7	600	300	3	600	900	1800	180	120	600	t	t	t	f	30	critical	2026-02-25 18:34:50.327107+00	2026-02-25 18:34:50.327107+00
2	1	600	300	3	600	900	1800	180	120	600	t	t	t	f	30	critical	2026-02-25 18:34:50.327107+00	2026-02-25 18:34:50.327107+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: coruja
--

COPY public.users (id, tenant_id, email, hashed_password, full_name, role, is_active, language, created_at, mfa_enabled, mfa_secret, mfa_backup_codes) FROM stdin;
1	1	admin@coruja.com	$2b$12$9b93PKKi9goAfecDTWrHPunjkiM28eKgBZ7Ww/PBG6r4exFdPY2f6	Administrator	admin	t	pt-BR	2026-02-11 17:42:50.924435+00	t	DLRGJJSGGNLZV4DRP6DTG5C235VN3OMH	["3444-8274", "8979-3708", "8748-7238", "7575-0023", "5630-8938", "7040-7808", "6932-6204", "3257-1786", "9673-6813", "1472-0802"]
\.


--
-- Name: ai_analysis_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.ai_analysis_logs_id_seq', 1, false);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 1, false);


--
-- Name: authentication_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.authentication_config_id_seq', 1, true);


--
-- Name: auto_resolution_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.auto_resolution_config_id_seq', 1, true);


--
-- Name: custom_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.custom_reports_id_seq', 1, false);


--
-- Name: incidents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.incidents_id_seq', 272, true);


--
-- Name: knowledge_base_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.knowledge_base_id_seq', 199, true);


--
-- Name: kubernetes_alert_rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.kubernetes_alert_rules_id_seq', 5, true);


--
-- Name: kubernetes_alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.kubernetes_alerts_id_seq', 1, false);


--
-- Name: kubernetes_clusters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.kubernetes_clusters_id_seq', 1, false);


--
-- Name: kubernetes_metrics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.kubernetes_metrics_id_seq', 1, false);


--
-- Name: kubernetes_resources_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.kubernetes_resources_id_seq', 1, false);


--
-- Name: learning_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.learning_sessions_id_seq', 1, false);


--
-- Name: maintenance_windows_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.maintenance_windows_id_seq', 1, false);


--
-- Name: metrics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.metrics_id_seq', 188797, true);


--
-- Name: monthly_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.monthly_reports_id_seq', 1, false);


--
-- Name: probes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.probes_id_seq', 3, true);


--
-- Name: remediation_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.remediation_logs_id_seq', 261, true);


--
-- Name: resolution_attempts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.resolution_attempts_id_seq', 1, false);


--
-- Name: sensor_breach_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.sensor_breach_history_id_seq', 1, false);


--
-- Name: sensor_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.sensor_groups_id_seq', 6, true);


--
-- Name: sensor_notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.sensor_notes_id_seq', 5, true);


--
-- Name: sensors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.sensors_id_seq', 228, true);


--
-- Name: servers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.servers_id_seq', 11, true);


--
-- Name: tenants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.tenants_id_seq', 7, true);


--
-- Name: threshold_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.threshold_config_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coruja
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: ai_analysis_logs ai_analysis_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.ai_analysis_logs
    ADD CONSTRAINT ai_analysis_logs_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: authentication_config authentication_config_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.authentication_config
    ADD CONSTRAINT authentication_config_pkey PRIMARY KEY (id);


--
-- Name: authentication_config authentication_config_tenant_id_key; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.authentication_config
    ADD CONSTRAINT authentication_config_tenant_id_key UNIQUE (tenant_id);


--
-- Name: auto_resolution_config auto_resolution_config_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.auto_resolution_config
    ADD CONSTRAINT auto_resolution_config_pkey PRIMARY KEY (id);


--
-- Name: auto_resolution_config auto_resolution_config_tenant_id_key; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.auto_resolution_config
    ADD CONSTRAINT auto_resolution_config_tenant_id_key UNIQUE (tenant_id);


--
-- Name: custom_reports custom_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.custom_reports
    ADD CONSTRAINT custom_reports_pkey PRIMARY KEY (id);


--
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (id);


--
-- Name: knowledge_base knowledge_base_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.knowledge_base
    ADD CONSTRAINT knowledge_base_pkey PRIMARY KEY (id);


--
-- Name: kubernetes_alert_rules kubernetes_alert_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_alert_rules
    ADD CONSTRAINT kubernetes_alert_rules_pkey PRIMARY KEY (id);


--
-- Name: kubernetes_alerts kubernetes_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_alerts
    ADD CONSTRAINT kubernetes_alerts_pkey PRIMARY KEY (id);


--
-- Name: kubernetes_clusters kubernetes_clusters_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_clusters
    ADD CONSTRAINT kubernetes_clusters_pkey PRIMARY KEY (id);


--
-- Name: kubernetes_metrics kubernetes_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_metrics
    ADD CONSTRAINT kubernetes_metrics_pkey PRIMARY KEY (id);


--
-- Name: kubernetes_resources kubernetes_resources_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_resources
    ADD CONSTRAINT kubernetes_resources_pkey PRIMARY KEY (id);


--
-- Name: learning_sessions learning_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.learning_sessions
    ADD CONSTRAINT learning_sessions_pkey PRIMARY KEY (id);


--
-- Name: maintenance_windows maintenance_windows_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.maintenance_windows
    ADD CONSTRAINT maintenance_windows_pkey PRIMARY KEY (id);


--
-- Name: metrics metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.metrics
    ADD CONSTRAINT metrics_pkey PRIMARY KEY (id);


--
-- Name: monthly_reports monthly_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.monthly_reports
    ADD CONSTRAINT monthly_reports_pkey PRIMARY KEY (id);


--
-- Name: probes probes_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.probes
    ADD CONSTRAINT probes_pkey PRIMARY KEY (id);


--
-- Name: remediation_logs remediation_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.remediation_logs
    ADD CONSTRAINT remediation_logs_pkey PRIMARY KEY (id);


--
-- Name: resolution_attempts resolution_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.resolution_attempts
    ADD CONSTRAINT resolution_attempts_pkey PRIMARY KEY (id);


--
-- Name: sensor_breach_history sensor_breach_history_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_breach_history
    ADD CONSTRAINT sensor_breach_history_pkey PRIMARY KEY (id);


--
-- Name: sensor_groups sensor_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_groups
    ADD CONSTRAINT sensor_groups_pkey PRIMARY KEY (id);


--
-- Name: sensor_notes sensor_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_notes
    ADD CONSTRAINT sensor_notes_pkey PRIMARY KEY (id);


--
-- Name: sensors sensors_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensors_pkey PRIMARY KEY (id);


--
-- Name: servers servers_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.servers
    ADD CONSTRAINT servers_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: threshold_config threshold_config_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.threshold_config
    ADD CONSTRAINT threshold_config_pkey PRIMARY KEY (id);


--
-- Name: threshold_config threshold_config_tenant_id_key; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.threshold_config
    ADD CONSTRAINT threshold_config_tenant_id_key UNIQUE (tenant_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_auth_config_tenant; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_auth_config_tenant ON public.authentication_config USING btree (tenant_id);


--
-- Name: idx_breach_history_active; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_breach_history_active ON public.sensor_breach_history USING btree (sensor_id, breach_end) WHERE (breach_end IS NULL);


--
-- Name: idx_breach_history_sensor; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_breach_history_sensor ON public.sensor_breach_history USING btree (sensor_id);


--
-- Name: idx_breach_history_start; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_breach_history_start ON public.sensor_breach_history USING btree (breach_start);


--
-- Name: idx_custom_reports_tenant; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_custom_reports_tenant ON public.custom_reports USING btree (tenant_id);


--
-- Name: idx_custom_reports_type; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_custom_reports_type ON public.custom_reports USING btree (report_type);


--
-- Name: idx_custom_reports_user; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_custom_reports_user ON public.custom_reports USING btree (user_id);


--
-- Name: idx_k8s_alert_rules_active; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_alert_rules_active ON public.kubernetes_alert_rules USING btree (is_active);


--
-- Name: idx_k8s_alert_rules_tenant; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_alert_rules_tenant ON public.kubernetes_alert_rules USING btree (tenant_id);


--
-- Name: idx_k8s_alerts_cluster; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_alerts_cluster ON public.kubernetes_alerts USING btree (cluster_id);


--
-- Name: idx_k8s_alerts_created; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_alerts_created ON public.kubernetes_alerts USING btree (created_at);


--
-- Name: idx_k8s_alerts_severity; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_alerts_severity ON public.kubernetes_alerts USING btree (severity);


--
-- Name: idx_k8s_alerts_status; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_alerts_status ON public.kubernetes_alerts USING btree (status);


--
-- Name: idx_k8s_clusters_active; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_clusters_active ON public.kubernetes_clusters USING btree (is_active);


--
-- Name: idx_k8s_clusters_probe; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_clusters_probe ON public.kubernetes_clusters USING btree (probe_id);


--
-- Name: idx_k8s_clusters_tenant; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_clusters_tenant ON public.kubernetes_clusters USING btree (tenant_id);


--
-- Name: idx_k8s_metrics_resource; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_metrics_resource ON public.kubernetes_metrics USING btree (resource_id);


--
-- Name: idx_k8s_metrics_timestamp; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_metrics_timestamp ON public.kubernetes_metrics USING btree ("timestamp");


--
-- Name: idx_k8s_resources_cluster; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_resources_cluster ON public.kubernetes_resources USING btree (cluster_id);


--
-- Name: idx_k8s_resources_namespace; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_resources_namespace ON public.kubernetes_resources USING btree (namespace);


--
-- Name: idx_k8s_resources_status; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_resources_status ON public.kubernetes_resources USING btree (status);


--
-- Name: idx_k8s_resources_type; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_resources_type ON public.kubernetes_resources USING btree (resource_type);


--
-- Name: idx_k8s_resources_uid; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_k8s_resources_uid ON public.kubernetes_resources USING btree (uid);


--
-- Name: idx_kb_signature; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_kb_signature ON public.knowledge_base USING btree (problem_signature);


--
-- Name: idx_kb_success_rate; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_kb_success_rate ON public.knowledge_base USING btree (success_rate);


--
-- Name: idx_kb_tenant_sensor; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_kb_tenant_sensor ON public.knowledge_base USING btree (tenant_id, sensor_type);


--
-- Name: idx_learning_created; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_learning_created ON public.learning_sessions USING btree (created_at);


--
-- Name: idx_learning_incident; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_learning_incident ON public.learning_sessions USING btree (incident_id);


--
-- Name: idx_learning_tenant; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_learning_tenant ON public.learning_sessions USING btree (tenant_id);


--
-- Name: idx_maintenance_window_server; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_maintenance_window_server ON public.maintenance_windows USING btree (server_id);


--
-- Name: idx_maintenance_window_tenant; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_maintenance_window_tenant ON public.maintenance_windows USING btree (tenant_id);


--
-- Name: idx_maintenance_window_time; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_maintenance_window_time ON public.maintenance_windows USING btree (start_time, end_time);


--
-- Name: idx_metrics_sensor_timestamp; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_metrics_sensor_timestamp ON public.metrics USING btree (sensor_id, "timestamp");


--
-- Name: idx_metrics_timestamp; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_metrics_timestamp ON public.metrics USING btree ("timestamp");


--
-- Name: idx_monthly_report_tenant_period; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_monthly_report_tenant_period ON public.monthly_reports USING btree (tenant_id, year, month);


--
-- Name: idx_resolution_created; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_resolution_created ON public.resolution_attempts USING btree (created_at);


--
-- Name: idx_resolution_status; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_resolution_status ON public.resolution_attempts USING btree (status);


--
-- Name: idx_resolution_tenant_incident; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_resolution_tenant_incident ON public.resolution_attempts USING btree (tenant_id, incident_id);


--
-- Name: idx_sensor_groups_parent; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_sensor_groups_parent ON public.sensor_groups USING btree (parent_id);


--
-- Name: idx_sensor_groups_tenant; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_sensor_groups_tenant ON public.sensor_groups USING btree (tenant_id);


--
-- Name: idx_sensors_group; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_sensors_group ON public.sensors USING btree (group_id);


--
-- Name: idx_sensors_probe_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_sensors_probe_id ON public.sensors USING btree (probe_id);


--
-- Name: idx_threshold_config_tenant; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX idx_threshold_config_tenant ON public.threshold_config USING btree (tenant_id);


--
-- Name: ix_ai_analysis_logs_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_ai_analysis_logs_id ON public.ai_analysis_logs USING btree (id);


--
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_authentication_config_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_authentication_config_id ON public.authentication_config USING btree (id);


--
-- Name: ix_auto_resolution_config_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_auto_resolution_config_id ON public.auto_resolution_config USING btree (id);


--
-- Name: ix_custom_reports_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_custom_reports_id ON public.custom_reports USING btree (id);


--
-- Name: ix_incidents_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_incidents_id ON public.incidents USING btree (id);


--
-- Name: ix_knowledge_base_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_knowledge_base_id ON public.knowledge_base USING btree (id);


--
-- Name: ix_knowledge_base_problem_signature; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_knowledge_base_problem_signature ON public.knowledge_base USING btree (problem_signature);


--
-- Name: ix_knowledge_base_sensor_type; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_knowledge_base_sensor_type ON public.knowledge_base USING btree (sensor_type);


--
-- Name: ix_kubernetes_clusters_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_kubernetes_clusters_id ON public.kubernetes_clusters USING btree (id);


--
-- Name: ix_kubernetes_metrics_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_kubernetes_metrics_id ON public.kubernetes_metrics USING btree (id);


--
-- Name: ix_kubernetes_metrics_timestamp; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_kubernetes_metrics_timestamp ON public.kubernetes_metrics USING btree ("timestamp");


--
-- Name: ix_kubernetes_resources_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_kubernetes_resources_id ON public.kubernetes_resources USING btree (id);


--
-- Name: ix_learning_sessions_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_learning_sessions_id ON public.learning_sessions USING btree (id);


--
-- Name: ix_maintenance_windows_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_maintenance_windows_id ON public.maintenance_windows USING btree (id);


--
-- Name: ix_metrics_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_metrics_id ON public.metrics USING btree (id);


--
-- Name: ix_metrics_timestamp; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_metrics_timestamp ON public.metrics USING btree ("timestamp");


--
-- Name: ix_monthly_reports_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_monthly_reports_id ON public.monthly_reports USING btree (id);


--
-- Name: ix_probes_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_probes_id ON public.probes USING btree (id);


--
-- Name: ix_probes_token; Type: INDEX; Schema: public; Owner: coruja
--

CREATE UNIQUE INDEX ix_probes_token ON public.probes USING btree (token);


--
-- Name: ix_remediation_logs_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_remediation_logs_id ON public.remediation_logs USING btree (id);


--
-- Name: ix_resolution_attempts_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_resolution_attempts_id ON public.resolution_attempts USING btree (id);


--
-- Name: ix_sensor_notes_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_sensor_notes_id ON public.sensor_notes USING btree (id);


--
-- Name: ix_sensors_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_sensors_id ON public.sensors USING btree (id);


--
-- Name: ix_servers_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_servers_id ON public.servers USING btree (id);


--
-- Name: ix_tenants_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_tenants_id ON public.tenants USING btree (id);


--
-- Name: ix_tenants_slug; Type: INDEX; Schema: public; Owner: coruja
--

CREATE UNIQUE INDEX ix_tenants_slug ON public.tenants USING btree (slug);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: coruja
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: coruja
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ai_analysis_logs ai_analysis_logs_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.ai_analysis_logs
    ADD CONSTRAINT ai_analysis_logs_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id);


--
-- Name: audit_logs audit_logs_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: authentication_config authentication_config_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.authentication_config
    ADD CONSTRAINT authentication_config_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: auto_resolution_config auto_resolution_config_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.auto_resolution_config
    ADD CONSTRAINT auto_resolution_config_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: custom_reports custom_reports_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.custom_reports
    ADD CONSTRAINT custom_reports_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: custom_reports custom_reports_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.custom_reports
    ADD CONSTRAINT custom_reports_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: incidents incidents_acknowledged_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_acknowledged_by_fkey FOREIGN KEY (acknowledged_by) REFERENCES public.users(id);


--
-- Name: incidents incidents_sensor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_sensor_id_fkey FOREIGN KEY (sensor_id) REFERENCES public.sensors(id);


--
-- Name: knowledge_base knowledge_base_learned_from_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.knowledge_base
    ADD CONSTRAINT knowledge_base_learned_from_incident_id_fkey FOREIGN KEY (learned_from_incident_id) REFERENCES public.incidents(id);


--
-- Name: knowledge_base knowledge_base_learned_from_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.knowledge_base
    ADD CONSTRAINT knowledge_base_learned_from_user_id_fkey FOREIGN KEY (learned_from_user_id) REFERENCES public.users(id);


--
-- Name: knowledge_base knowledge_base_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.knowledge_base
    ADD CONSTRAINT knowledge_base_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: kubernetes_alert_rules kubernetes_alert_rules_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_alert_rules
    ADD CONSTRAINT kubernetes_alert_rules_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.kubernetes_clusters(id) ON DELETE CASCADE;


--
-- Name: kubernetes_alert_rules kubernetes_alert_rules_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_alert_rules
    ADD CONSTRAINT kubernetes_alert_rules_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: kubernetes_alerts kubernetes_alerts_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_alerts
    ADD CONSTRAINT kubernetes_alerts_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.kubernetes_clusters(id) ON DELETE CASCADE;


--
-- Name: kubernetes_alerts kubernetes_alerts_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_alerts
    ADD CONSTRAINT kubernetes_alerts_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.kubernetes_resources(id) ON DELETE CASCADE;


--
-- Name: kubernetes_clusters kubernetes_clusters_probe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_clusters
    ADD CONSTRAINT kubernetes_clusters_probe_id_fkey FOREIGN KEY (probe_id) REFERENCES public.probes(id);


--
-- Name: kubernetes_clusters kubernetes_clusters_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_clusters
    ADD CONSTRAINT kubernetes_clusters_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: kubernetes_metrics kubernetes_metrics_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_metrics
    ADD CONSTRAINT kubernetes_metrics_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.kubernetes_resources(id);


--
-- Name: kubernetes_resources kubernetes_resources_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.kubernetes_resources
    ADD CONSTRAINT kubernetes_resources_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.kubernetes_clusters(id);


--
-- Name: learning_sessions learning_sessions_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.learning_sessions
    ADD CONSTRAINT learning_sessions_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id);


--
-- Name: learning_sessions learning_sessions_knowledge_base_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.learning_sessions
    ADD CONSTRAINT learning_sessions_knowledge_base_id_fkey FOREIGN KEY (knowledge_base_id) REFERENCES public.knowledge_base(id);


--
-- Name: learning_sessions learning_sessions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.learning_sessions
    ADD CONSTRAINT learning_sessions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: learning_sessions learning_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.learning_sessions
    ADD CONSTRAINT learning_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: maintenance_windows maintenance_windows_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.maintenance_windows
    ADD CONSTRAINT maintenance_windows_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: maintenance_windows maintenance_windows_server_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.maintenance_windows
    ADD CONSTRAINT maintenance_windows_server_id_fkey FOREIGN KEY (server_id) REFERENCES public.servers(id);


--
-- Name: maintenance_windows maintenance_windows_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.maintenance_windows
    ADD CONSTRAINT maintenance_windows_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: metrics metrics_sensor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.metrics
    ADD CONSTRAINT metrics_sensor_id_fkey FOREIGN KEY (sensor_id) REFERENCES public.sensors(id);


--
-- Name: monthly_reports monthly_reports_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.monthly_reports
    ADD CONSTRAINT monthly_reports_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: probes probes_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.probes
    ADD CONSTRAINT probes_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: remediation_logs remediation_logs_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.remediation_logs
    ADD CONSTRAINT remediation_logs_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id);


--
-- Name: resolution_attempts resolution_attempts_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.resolution_attempts
    ADD CONSTRAINT resolution_attempts_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: resolution_attempts resolution_attempts_feedback_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.resolution_attempts
    ADD CONSTRAINT resolution_attempts_feedback_by_fkey FOREIGN KEY (feedback_by) REFERENCES public.users(id);


--
-- Name: resolution_attempts resolution_attempts_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.resolution_attempts
    ADD CONSTRAINT resolution_attempts_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id);


--
-- Name: resolution_attempts resolution_attempts_knowledge_base_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.resolution_attempts
    ADD CONSTRAINT resolution_attempts_knowledge_base_id_fkey FOREIGN KEY (knowledge_base_id) REFERENCES public.knowledge_base(id);


--
-- Name: resolution_attempts resolution_attempts_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.resolution_attempts
    ADD CONSTRAINT resolution_attempts_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: sensor_breach_history sensor_breach_history_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_breach_history
    ADD CONSTRAINT sensor_breach_history_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id);


--
-- Name: sensor_breach_history sensor_breach_history_sensor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_breach_history
    ADD CONSTRAINT sensor_breach_history_sensor_id_fkey FOREIGN KEY (sensor_id) REFERENCES public.sensors(id) ON DELETE CASCADE;


--
-- Name: sensor_groups sensor_groups_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_groups
    ADD CONSTRAINT sensor_groups_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.sensor_groups(id) ON DELETE CASCADE;


--
-- Name: sensor_groups sensor_groups_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_groups
    ADD CONSTRAINT sensor_groups_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: sensor_notes sensor_notes_sensor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_notes
    ADD CONSTRAINT sensor_notes_sensor_id_fkey FOREIGN KEY (sensor_id) REFERENCES public.sensors(id);


--
-- Name: sensor_notes sensor_notes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensor_notes
    ADD CONSTRAINT sensor_notes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: sensors sensors_acknowledged_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensors_acknowledged_by_fkey FOREIGN KEY (acknowledged_by) REFERENCES public.users(id);


--
-- Name: sensors sensors_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensors_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.sensor_groups(id);


--
-- Name: sensors sensors_last_note_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensors_last_note_by_fkey FOREIGN KEY (last_note_by) REFERENCES public.users(id);


--
-- Name: sensors sensors_probe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensors_probe_id_fkey FOREIGN KEY (probe_id) REFERENCES public.probes(id);


--
-- Name: sensors sensors_server_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensors_server_id_fkey FOREIGN KEY (server_id) REFERENCES public.servers(id);


--
-- Name: servers servers_probe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.servers
    ADD CONSTRAINT servers_probe_id_fkey FOREIGN KEY (probe_id) REFERENCES public.probes(id);


--
-- Name: servers servers_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.servers
    ADD CONSTRAINT servers_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: threshold_config threshold_config_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.threshold_config
    ADD CONSTRAINT threshold_config_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: users users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coruja
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: coruja
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict 9WtFILhCaPdQFb7GJYmpobzOACliv5QhvOsI5WlR3zB7I8evhvuBz4Mjr0rtA2A

