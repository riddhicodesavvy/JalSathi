export const percent = (value: number) => `${(value * 100).toFixed(1)}%`;
export const friendly = (value: string) =>
  value === "ph" ? "pH" : value.replaceAll("_", " ");
