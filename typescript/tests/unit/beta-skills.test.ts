import { BetaSkillsService } from "../../src/beta-skills";
import * as sinon from "sinon";

describe("BetaSkillsService", () => {
  let service: BetaSkillsService;
  let mockAgentBay: any;
  let mockClient: any;
  let sandbox: sinon.SinonSandbox;

  beforeEach(() => {
    sandbox = sinon.createSandbox();

    mockClient = {
      getSkillMetaData: sandbox.stub(),
      listSkillMetaData: sandbox.stub(),
    };

    mockAgentBay = {
      getAPIKey: sandbox.stub().returns("test-api-key"),
      getClient: sandbox.stub().returns(mockClient),
    };

    service = new BetaSkillsService(mockAgentBay);
  });

  afterEach(() => {
    sandbox.restore();
  });

  describe("getMetadata", () => {
    it("should parse response into SkillsMetadataResult", async () => {
      mockClient.getSkillMetaData.resolves({
        body: {
          success: true,
          data: {
            skillPath: "/home/wuying/skills",
            metaDataList: [
              { name: "pdf", description: "PDF processing skill" },
              { name: "docx", description: "Word document skill" },
            ],
          },
        },
      });

      const result = await service.getMetadata();

      expect(result.skillsRootPath).toBe("/home/wuying/skills");
      expect(result.skills).toHaveLength(2);
      expect(result.skills[0].name).toBe("pdf");
      expect(result.skills[0].description).toBe("PDF processing skill");
      expect(result.skills[1].name).toBe("docx");
      expect(result.skills[1].description).toBe("Word document skill");
    });

    it("should pass imageId and skillNames to request", async () => {
      mockClient.getSkillMetaData.resolves({
        body: {
          success: true,
          data: {
            skillPath: "/skills",
            metaDataList: [],
          },
        },
      });

      await service.getMetadata({
        imageId: "my-image",
        skillNames: ["grp-001", "grp-002"],
      });

      const call = mockClient.getSkillMetaData.getCall(0);
      const request = call.args[0];
      expect(request.authorization).toBe("Bearer test-api-key");
      expect(request.imageId).toBe("my-image");
      expect(request.skillGroupIds).toEqual(["grp-001", "grp-002"]);
    });

    it("should raise when API returns success=false", async () => {
      mockClient.getSkillMetaData.resolves({
        body: {
          success: false,
          code: "InvalidRequest",
          message: "Bad group id",
        },
      });

      await expect(service.getMetadata()).rejects.toThrow(
        "GetSkillMetaData failed"
      );
    });

    it("should skip items with empty names", async () => {
      mockClient.getSkillMetaData.resolves({
        body: {
          success: true,
          data: {
            skillPath: "/skills",
            metaDataList: [
              { name: "", description: "Should be skipped" },
              { name: "valid-skill", description: "Valid" },
            ],
          },
        },
      });

      const result = await service.getMetadata();

      expect(result.skills).toHaveLength(1);
      expect(result.skills[0].name).toBe("valid-skill");
    });

    it("should return empty skills when metaDataList is null", async () => {
      mockClient.getSkillMetaData.resolves({
        body: {
          success: true,
          data: {
            skillPath: "/skills",
            metaDataList: null,
          },
        },
      });

      const result = await service.getMetadata();

      expect(result.skills).toHaveLength(0);
      expect(result.skillsRootPath).toBe("/skills");
    });

    it("should raise when Data field is missing", async () => {
      mockClient.getSkillMetaData.resolves({
        body: {
          success: true,
          data: null,
        },
      });

      await expect(service.getMetadata()).rejects.toThrow(
        "GetSkillMetaData failed: missing Data field"
      );
    });
  });

  describe("listMetadata (deprecated)", () => {
    it("should still work for backward compatibility", async () => {
      mockClient.listSkillMetaData.resolves({
        body: {
          success: true,
          data: [{ name: "skill1", description: "Skill 1" }],
        },
      });

      const result = await service.listMetadata();

      expect(result).toHaveLength(1);
      expect(result[0].name).toBe("skill1");
    });
  });
});
