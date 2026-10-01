export type ImportedVideo = {
  uri: string;
  fileName: string;
  durationSeconds: number | null;
  width: number;
  height: number;
  fileSizeBytes?: number;
};
