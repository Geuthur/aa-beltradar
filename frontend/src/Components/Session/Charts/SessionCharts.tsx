// React
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';

// AA Belt Radar
import { loadSnapshot } from '@/Api/BeltRadar';
import { queryKeys } from '@/Api/query';
import type { ApexChartSchema } from '@/Api/schema';
import { MiningChart } from '@/Components/Session/Charts/MiningChart';
import { TrafficChart } from '@/Components/Session/Charts/TrafficChart';

export interface SessionChartsProps {
    charts?: ApexChartSchema | null;
    traffic?: ApexChartSchema | null;
    isLoading?: boolean;
}

export function SessionCharts({ charts, traffic, isLoading: propIsLoading }: SessionChartsProps) {
    const { publicID } = useParams();

    const shouldQuery = charts === undefined && traffic === undefined;

    const { data: snapshotData, isLoading: queryIsLoading } = useQuery({
        queryKey: queryKeys.Snapshot(String(publicID)),
        queryFn: () => loadSnapshot(String(publicID)),
        refetchOnWindowFocus: false,
        enabled: !!publicID && shouldQuery,
    });

    const isLoading = propIsLoading ?? (shouldQuery ? queryIsLoading : false);
    const chartsData = charts ?? snapshotData?.charts;
    const trafficData = traffic ?? snapshotData?.traffic;

    return (
        <section aria-label="Session Charts" className="row mt-2">
            <div className="col-md-6 mb-2">
                <div className="card card-body rounded h-100">
                    <MiningChart data={chartsData} isLoading={isLoading} />
                </div>
            </div>
            <div className="col-md-6 mb-2">
                <div className="card card-body rounded h-100">
                    <TrafficChart data={trafficData} isLoading={isLoading} />
                </div>
            </div>
        </section>
    );
}

export default SessionCharts;
