import { AgentBay } from "../../src/agent-bay";
import { log } from "../../src/utils/logger";

describe("Beta volume integration tests", () => {
  test(
    "should create/list/mount/delete volume end-to-end",
    async () => {
      const apiKey = process.env.AGENTBAY_API_KEY;
      if (!apiKey) {
        throw new Error("AGENTBAY_API_KEY environment variable is not set");
      }

      const agentBay = new AgentBay({ apiKey });
      const imageId = "imgc-0ab5ta4mgqs15qxjf";
      const volumeName = `beta-volume-it-${Date.now()}`;

      const volResult = await agentBay.betaVolume.create(volumeName, imageId);
      expect(volResult.success).toBe(true);
      expect(volResult.volume?.id).toBeTruthy();

      const volumeId = volResult.volume!.id;

      try {
        const listResult = await agentBay.betaVolume.list({
          imageId,
          maxResults: 10,
          volumeName,
        });
        expect(listResult.success).toBe(true);
        expect(listResult.volumes.some((v) => v.id === volumeId)).toBe(true);

        log("Creating a new session with mounted volume...");
        const createResult = await agentBay.create({
          imageId,
          betaVolumeId: volumeId,
          labels: { "test-type": "beta-volume-integration" },
        });
        expect(createResult.success).toBe(true);
        expect(createResult.session?.token).toBeTruthy();

        if (createResult.session) {
          await createResult.session.delete();
        }
      } finally {
        const del = await agentBay.betaVolume.delete(volumeId);
        expect(del.success).toBe(true);
      }
    },
    120_000
  );
});


