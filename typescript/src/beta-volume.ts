import { AgentBay } from "./agent-bay";
import {
  DeleteVolumeRequest,
  GetVolumeRequest,
  ListVolumesRequest,
} from "./api/models/model";
import {
  logAPICall,
  logAPIResponseWithDetails,
  logOperationError,
} from "./utils/logger";

/**
 * Block storage volume (data disk).
 *
 * Note: This is a beta feature and may change in future releases.
 */
export interface Volume {
  id: string;
  name: string;
  status?: string;
}

export interface VolumeResult {
  requestId: string;
  success: boolean;
  volume?: Volume;
  errorMessage?: string;
}

export interface VolumeListResult {
  requestId: string;
  success: boolean;
  volumes: Volume[];
  nextToken?: string;
  maxResults?: number;
  totalCount?: number;
  errorMessage?: string;
}

export class BetaVolumeService {
  constructor(private agentBay: AgentBay) {}

  async create(name: string, imageId: string): Promise<VolumeResult> {
    return await this.get({ name, create: true, imageId });
  }

  async get(params: {
    volumeId?: string;
    name?: string;
    create?: boolean;
    imageId: string;
  }): Promise<VolumeResult> {
    const { volumeId, name, create, imageId } = params;
    if (!imageId) {
      throw new Error("imageId is required");
    }

    // Get by ID -> ListVolumes(volumeIds=[id])
    if (volumeId) {
      const list = await this.list({
        imageId,
        maxResults: 10,
        volumeIds: [volumeId],
      });
      if (!list.success) {
        return {
          requestId: list.requestId,
          success: false,
          volume: undefined,
          errorMessage: list.errorMessage,
        };
      }
      const v = list.volumes[0];
      if (!v) {
        return {
          requestId: list.requestId,
          success: false,
          volume: undefined,
          errorMessage: "Volume not found",
        };
      }
      return { requestId: list.requestId, success: true, volume: v };
    }

    if (!name) {
      throw new Error("Either volumeId or name is required");
    }

    const req = new GetVolumeRequest({
      authorization: "Bearer " + (this.agentBay as any).apiKey,
      allowCreate: create ?? false,
      imageId,
      volumeName: name,
    });

    logAPICall("GetVolume(beta)", { volumeName: name, allowCreate: !!create, imageId });
    const resp = await this.agentBay.client.getVolume(req);

    const requestId = resp?.body?.requestId || "";
    const success = !!resp?.body?.success;
    if (!success && resp?.body?.code) {
      return {
        requestId,
        success: false,
        volume: undefined,
        errorMessage: `[${resp.body.code}] ${resp.body.message || "Unknown error"}`,
      };
    }

    const data = resp?.body?.data;
    const vid = data?.volumeId || "";
    if (!vid) {
      logAPIResponseWithDetails("GetVolume(beta)", requestId, false, {}, JSON.stringify(resp?.body || {}));
      return {
        requestId,
        success: false,
        volume: undefined,
        errorMessage: "VolumeId not found in response",
      };
    }

    const volume: Volume = {
      id: vid,
      name: data?.volumeName || "",
      status: data?.status || "",
    };

    logAPIResponseWithDetails("GetVolume(beta)", requestId, true, { volume_id: vid }, JSON.stringify(resp?.body || {}));
    return { requestId, success: true, volume };
  }

  async list(params: {
    imageId: string;
    maxResults?: number;
    nextToken?: string;
    volumeIds?: string[];
    volumeName?: string;
  }): Promise<VolumeListResult> {
    const { imageId, maxResults, nextToken, volumeIds, volumeName } = params;
    if (!imageId) {
      throw new Error("imageId is required");
    }

    const req = new ListVolumesRequest({
      authorization: "Bearer " + (this.agentBay as any).apiKey,
      imageId,
      maxResults: maxResults ?? 10,
      nextToken: nextToken || undefined,
      volumeIds,
      volumeName: volumeName || undefined,
    });

    logAPICall("ListVolumes(beta)", { imageId, maxResults: maxResults ?? 10 });
    const resp = await this.agentBay.client.listVolumes(req);

    const requestId = resp?.body?.requestId || "";
    const success = !!resp?.body?.success;
    if (!success && resp?.body?.code) {
      return {
        requestId,
        success: false,
        volumes: [],
        errorMessage: `[${resp.body.code}] ${resp.body.message || "Unknown error"}`,
      };
    }

    const volumes: Volume[] = (resp?.body?.data || [])
      .filter((it) => !!it?.volumeId)
      .map((it) => ({
        id: it.volumeId!,
        name: it.volumeName || "",
        status: it.status || "",
      }));

    return {
      requestId,
      success: true,
      volumes,
      nextToken: resp?.body?.nextToken,
      maxResults: resp?.body?.maxResults,
      totalCount: volumes.length,
      errorMessage: "",
    };
  }

  async delete(volumeId: string): Promise<{ requestId: string; success: boolean; errorMessage?: string }> {
    if (!volumeId) {
      throw new Error("volumeId is required");
    }

    const req = new DeleteVolumeRequest({
      authorization: "Bearer " + (this.agentBay as any).apiKey,
      volumeId,
    });

    logAPICall("DeleteVolume(beta)", { volumeId });
    try {
      const resp = await this.agentBay.client.deleteVolume(req);
      const requestId = resp?.body?.requestId || "";
      const success = !!resp?.body?.success;
      if (!success && resp?.body?.code) {
        return {
          requestId,
          success: false,
          errorMessage: `[${resp.body.code}] ${resp.body.message || "Unknown error"}`,
        };
      }
      return { requestId, success: true };
    } catch (e: any) {
      logOperationError("DeleteVolume(beta)", String(e), true);
      return { requestId: "", success: false, errorMessage: String(e) };
    }
  }
}


