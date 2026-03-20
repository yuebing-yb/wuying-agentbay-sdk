package com.aliyun.agentbay.skills;

import java.util.List;

/**
 * Result of GetSkillMetaData containing skills list and skills root path.
 */
public class SkillsMetadataResult {
    private final List<SkillMetadata> skills;
    private final String skillsRootPath;

    public SkillsMetadataResult(List<SkillMetadata> skills, String skillsRootPath) {
        this.skills = skills;
        this.skillsRootPath = skillsRootPath != null ? skillsRootPath : "";
    }

    public List<SkillMetadata> getSkills() {
        return skills;
    }

    public String getSkillsRootPath() {
        return skillsRootPath;
    }
}
