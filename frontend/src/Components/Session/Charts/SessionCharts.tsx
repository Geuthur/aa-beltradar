// React
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { Card } from 'react-bootstrap';

// AA Belt Radar
import { loadSnapshot } from '@/Api/ApiCalls';
import { queryKeys, SESSION_REFETCH_INTERVAL_MS } from '@/Api/query';
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
        refetchInterval: SESSION_REFETCH_INTERVAL_MS,
        enabled: !!publicID && shouldQuery,
    });

    const isLoading = propIsLoading ?? (shouldQuery ? queryIsLoading : false);
    const chartsData = charts ?? snapshotData?.charts;
    const trafficData = traffic ?? snapshotData?.traffic;

    return (
        <div aria-label="Session Charts" className="row g-3">
            <div className="col-md-6">
                <Card className="bg-secondary text-light border-0 shadow-sm h-100">
                    <Card.Body>
                        <MiningChart data={chartsData} isLoading={isLoading} />
                    </Card.Body>
                </Card>
            </div>
            <div className="col-md-6">
                <Card className="bg-secondary text-light border-0 shadow-sm h-100">
                    <Card.Body>
                        <TrafficChart data={trafficData} isLoading={isLoading} />
                    </Card.Body>
                </Card>
            </div>
        </div>
    );
}

export default SessionCharts;
