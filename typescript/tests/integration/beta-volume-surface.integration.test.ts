import { Client } from "../../src/api/client";
import { CreateMcpSessionRequest } from "../../src/api/models/CreateMcpSessionRequest";

describe("Beta volume surface compatibility tests", () => {
  test("mcp api client should expose volume APIs", () => {
    for (const name of ["getVolume", "deleteVolume", "listVolumes"]) {
      expect(typeof (Client.prototype as any)[name]).toBe("function");
    }
  });

  test("CreateMcpSessionRequest should include volumeId field mapping", () => {
    const names = CreateMcpSessionRequest.names();
    expect(names.volumeId).toBe("VolumeId");
  });
});


