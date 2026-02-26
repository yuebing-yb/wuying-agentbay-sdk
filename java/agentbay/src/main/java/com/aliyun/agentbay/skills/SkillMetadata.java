package com.aliyun.agentbay.skills;

/**
 * Official skill metadata returned by BetaSkillsService.listMetadata().
 *
 * Notes:
 * - Backend currently returns name/description only.
 */
public class SkillMetadata {
    private final String name;
    private final String description;
    private final String dir;

    public SkillMetadata(String name, String description) {
        this(name, description, null);
    }

    public SkillMetadata(String name, String description, String dir) {
        this.name = name;
        this.description = description;
        this.dir = dir;
    }

    public String getName() {
        return name;
    }

    public String getDescription() {
        return description;
    }

    /**
     * Reserved for future use. Always null for ListSkillMetaData.
     */
    public String getDir() {
        return dir;
    }
}

