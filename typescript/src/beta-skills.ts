import { AgentBay } from "./agent-bay";
import * as $_client from "./api";
import { APIError } from "./exceptions";
import { logAPICall, logDebug } from "./utils/logger";

export interface SkillMetadataItem {
  name: string;
  description: string;
}

export interface SkillsMetadataResult {
  skills: SkillMetadataItem[];
  skillsRootPath: string;
}

export interface GetMetadataOptions {
  imageId?: string;
  skillNames?: string[];
}

/**
 * Beta skills service (trial feature).
 */
export class BetaSkillsService {
  private agentBay: AgentBay;

  constructor(agentBay: AgentBay) {
    this.agentBay = agentBay;
  }

  /**
   * Get skills metadata without starting a sandbox.
   *
   * @param options - Optional filtering parameters.
   * @param options.imageId - Image ID to determine the skills root path.
   * @param options.groupIds - Filter by skill group IDs.
   * @returns SkillsMetadataResult with skills list and skillsRootPath.
   */
  async getMetadata(
    options: GetMetadataOptions = {}
  ): Promise<SkillsMetadataResult> {
    const request = new $_client.GetSkillMetaDataRequest({
      authorization: `Bearer ${this.agentBay.getAPIKey()}`,
      imageId: options.imageId,
      skillGroupIds: options.skillNames,
    });

    const maxAttempts = 3;
    let delayMs = 200;
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        logAPICall("GetSkillMetaData(beta)");
        const response = await this.agentBay
          .getClient()
          .getSkillMetaData(request);

        if (!response.body || typeof response.body !== "object") {
          throw new APIError(
            "GetSkillMetaData failed: invalid response format"
          );
        }

        if (response.body.success === false) {
          const code = response.body.code ? `[${response.body.code}] ` : "";
          const msg = response.body.message || "Unknown error";
          throw new APIError(`GetSkillMetaData failed: ${code}${msg}`);
        }

        const data = response.body.data;
        if (!data) {
          throw new APIError("GetSkillMetaData failed: missing Data field");
        }

        const skillPath = String(data.skillPath || "");
        const metaDataList = data.metaDataList || [];

        const skills: SkillMetadataItem[] = [];
        for (const raw of metaDataList) {
          const name = String(raw?.name || "").trim();
          if (!name) {
            continue;
          }
          const description = String(raw?.description || "");
          skills.push({ name, description });
        }

        return { skills, skillsRootPath: skillPath };
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : `${error}`;
        logDebug(`GetSkillMetaData attempt ${attempt} failed: ${msg}`);
        if (
          attempt < maxAttempts &&
          (msg.includes("ServiceUnavailable") || msg.includes("503"))
        ) {
          await new Promise((resolve) => setTimeout(resolve, delayMs));
          delayMs *= 2;
          continue;
        }
        if (error instanceof APIError) {
          throw error;
        }
        throw new APIError(`GetSkillMetaData failed: ${msg}`);
      }
    }
    throw new APIError("GetSkillMetaData failed: exhausted retries");
  }

  /**
   * @deprecated Use getMetadata() instead.
   */
  async listMetadata(): Promise<SkillMetadataItem[]> {
    const request = new $_client.ListSkillMetaDataRequest({
      authorization: `Bearer ${this.agentBay.getAPIKey()}`,
    });

    const maxAttempts = 3;
    let delayMs = 200;
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        logAPICall("ListSkillMetaData(beta)");
        const response = await this.agentBay
          .getClient()
          .listSkillMetaData(request);

        if (!response.body || typeof response.body !== "object") {
          throw new APIError(
            "ListSkillMetaData(beta) failed: invalid response format"
          );
        }

        if (response.body.success === false) {
          const code = response.body.code ? `[${response.body.code}] ` : "";
          const msg = response.body.message || "Unknown error";
          throw new APIError(`ListSkillMetaData(beta) failed: ${code}${msg}`);
        }

        const data = response.body.data;
        if (!Array.isArray(data)) {
          throw new APIError(
            "ListSkillMetaData(beta) failed: invalid Data field"
          );
        }

        const items: SkillMetadataItem[] = [];
        for (const raw of data) {
          const name = String((raw as any)?.name || "").trim();
          if (!name) {
            continue;
          }
          const description = String((raw as any)?.description || "");
          items.push({ name, description });
        }
        return items;
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : `${error}`;
        logDebug(`ListSkillMetaData(beta) attempt ${attempt} failed: ${msg}`);
        if (
          attempt < maxAttempts &&
          (msg.includes("ServiceUnavailable") || msg.includes("503"))
        ) {
          await new Promise((resolve) => setTimeout(resolve, delayMs));
          delayMs *= 2;
          continue;
        }
        if (error instanceof APIError) {
          throw error;
        }
        throw new APIError(`ListSkillMetaData(beta) failed: ${msg}`);
      }
    }
    throw new APIError("ListSkillMetaData(beta) failed: exhausted retries");
  }
}
