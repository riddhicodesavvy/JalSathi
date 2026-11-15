import { z } from "zod";
export const sampleSchema = z.object({
  ph: z.number().min(0).max(14),
  Hardness: z.number().min(0).max(1e9),
  Solids: z.number().min(0).max(1e9),
  Chloramines: z.number().min(0).max(1e9),
  Sulfate: z.number().min(0).max(1e9),
  Conductivity: z.number().min(0).max(1e9),
  Organic_carbon: z.number().min(0).max(1e9),
  Trihalomethanes: z.number().min(0).max(1e9),
  Turbidity: z.number().min(0).max(1e9),
});
export type FormValues = z.infer<typeof sampleSchema>;
