package com.aliyun.agentbay.browser;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.module.jsonSchema.JsonSchema;
import com.fasterxml.jackson.module.jsonSchema.JsonSchemaGenerator;

import java.util.HashMap;
import java.util.Map;

/**
 * Options for browser extract operations - matches Python ExtractOptions
 * Generic type T represents the schema/result type (similar to Python's Generic[T])
 */
public class ExtractOptions<T> {
    private String instruction;
    private Class<T> schema;
    /** Alternative to schema class: provide raw JSON schema string directly. Java-only convenience field. */
    private String schemaJson;
    private Boolean useTextExtract;
    private Boolean useVision;
    private String selector;
    /** Timeout in seconds for the extract operation. */
    private Integer timeout;
    private Integer maxPage;

    public ExtractOptions(String instruction, Class<T> schema) {
        this.instruction = instruction;
        this.schema = schema;
    }

    public ExtractOptions(String instruction, String schemaJson) {
        this.instruction = instruction;
        this.schemaJson = schemaJson;
    }

    public ExtractOptions(String instruction, Class<T> schema, Boolean useTextExtract, Boolean useVision,
                         String selector, Integer timeout, Integer maxPage) {
        this.instruction = instruction;
        this.schema = schema;
        this.useTextExtract = useTextExtract;
        this.useVision = useVision;
        this.selector = selector;
        this.timeout = timeout;
        this.maxPage = maxPage;
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new HashMap<>();
        map.put("instruction", instruction);

        if (schemaJson != null) {
            map.put("field_schema", "schema: " + schemaJson);
        } else if (schema != null) {
            try {
                ObjectMapper mapper = new ObjectMapper();
                JsonSchemaGenerator schemaGen = new JsonSchemaGenerator(mapper);
                JsonSchema jsonSchema = schemaGen.generateSchema(schema);
                String schemaStr = mapper.writeValueAsString(jsonSchema);
                map.put("field_schema", "schema: " + schemaStr);
            } catch (Exception e) {
                throw new RuntimeException("Failed to generate schema from class: " + e.getMessage(), e);
            }
        }

        if (useTextExtract != null) map.put("use_text_extract", useTextExtract);
        if (useVision != null) map.put("use_vision", useVision);
        if (selector != null) map.put("selector", selector);
        if (timeout != null) map.put("timeout", timeout);
        if (maxPage != null) map.put("max_page", maxPage);
        return map;
    }

    // Getters and setters
    public String getInstruction() { return instruction; }
    public void setInstruction(String instruction) { this.instruction = instruction; }

    public Class<T> getSchema() { return schema; }
    public void setSchema(Class<T> schema) { this.schema = schema; }

    public String getSchemaJson() { return schemaJson; }
    public void setSchemaJson(String schemaJson) { this.schemaJson = schemaJson; }

    public Boolean getUseTextExtract() { return useTextExtract; }
    public void setUseTextExtract(Boolean useTextExtract) { this.useTextExtract = useTextExtract; }

    public Boolean getUseVision() { return useVision; }
    public void setUseVision(Boolean useVision) { this.useVision = useVision; }

    public String getSelector() { return selector; }
    public void setSelector(String selector) { this.selector = selector; }

    public Integer getTimeout() { return timeout; }
    public void setTimeout(Integer timeout) { this.timeout = timeout; }

    public Integer getMaxPage() { return maxPage; }
    public void setMaxPage(Integer maxPage) { this.maxPage = maxPage; }
}