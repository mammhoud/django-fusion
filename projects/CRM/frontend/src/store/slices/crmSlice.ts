// crmSlice — deals + pipeline state (Twenty DNA).
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export interface Deal {
  id: number;
  name: string;
  company: string;
  company_id: number | null;
  value: string;
  owner: string;
  expected_close_date: string;
  campaign: string | null;
}

export interface Stage {
  id: number;
  name: string;
  stage_type: string;
  color: string;
  probability: number;
  order: number;
  deals: Deal[];
}

export interface Pipeline {
  id: number;
  name: string;
  stages: Stage[];
}

interface CrmState {
  deals: Deal[];
  pipelines: Pipeline[];
  loading: boolean;
  activePipelineId: number | null;
}

const initialState: CrmState = { deals: [], pipelines: [], loading: false, activePipelineId: null };

const crmSlice = createSlice({
  name: 'crm',
  initialState,
  reducers: {
    setDeals(state, action: PayloadAction<Deal[]>) {
      state.deals = action.payload;
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
    setPipelines(state, action: PayloadAction<Pipeline[]>) {
      state.pipelines = action.payload;
      if (state.activePipelineId === null && action.payload.length > 0) {
        state.activePipelineId = action.payload[0].id;
      }
    },
    setActivePipeline(state, action: PayloadAction<number>) {
      state.activePipelineId = action.payload;
    },
    // Optimistic kanban drop: move a deal between stages of the active
    // pipeline in the store. The island rolls back by dispatching the
    // pre-drag snapshot via setPipelines if the move API rejects.
    moveDeal(state, action: PayloadAction<{ dealId: number; fromStageId: number; toStageId: number }>) {
      const { dealId, fromStageId, toStageId } = action.payload;
      for (const pipeline of state.pipelines) {
        const fromStage = pipeline.stages.find((stage) => stage.id === fromStageId);
        const toStage = pipeline.stages.find((stage) => stage.id === toStageId);
        if (!fromStage || !toStage || fromStage === toStage) continue;
        const idx = fromStage.deals.findIndex((deal) => deal.id === dealId);
        if (idx === -1) continue;
        const [deal] = fromStage.deals.splice(idx, 1);
        toStage.deals.push(deal);
      }
    },
  },
});

export const { setDeals, setLoading, setPipelines, setActivePipeline, moveDeal } = crmSlice.actions;
export default crmSlice.reducer;
