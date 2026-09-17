// React
import { useMemo } from 'react';

// Third Party
import type { ApexOptions } from 'apexcharts';
import Chart from 'react-apexcharts';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { ApexChartSchema } from '@/Api/schema';

export interface TrafficChartProps {
    data?: ApexChartSchema | null;
    isLoading?: boolean;
}

export function TrafficChart({ data, isLoading }: TrafficChartProps) {
    const { t } = useTranslation();

    // Translations for tooltips and titles
    const tMiningSpeed = t("Mining Speed");
    const tVolumeLeft = t("Volume Left (m³)");
    const tSpeed = t("Speed (m³/s)");
    const tNoData = t("No mining chart data available.");
    const tLoading = t("Loading...");

    const categories = useMemo(() => data?.categories ?? [], [data?.categories]);
    const series = useMemo(() => {
        return (data?.series ?? []).map((s) => ({
            name: s.name,
            type: s.type ?? (s.name.includes("Speed") ? 'line' : 'column'),
            data: s.data,
        }));
    }, [data?.series]);

    const options: ApexOptions = useMemo(
        () => ({
            chart: {
                type: 'line',
                height: 380,
                toolbar: { show: false },
            },
            stroke: {
                width: [0, 4],
                curve: 'smooth',
            },
            title: {
                text: tMiningSpeed,
            },
            dataLabels: {
                enabled: true,
                enabledOnSeries: [1],
                formatter: (val: string | number) => `${Number(val).toLocaleString()} m³/s`,
            },
            labels: categories,
            yaxis: [
                {
                    title: {
                        text: tVolumeLeft,
                    },
                    labels: {
                        formatter: (val: number) => Number(val).toLocaleString(),
                    },
                },
                {
                    opposite: true,
                    title: {
                        text: tSpeed,
                    },
                    labels: {
                        formatter: (val: number) => Number(val).toLocaleString(),
                    },
                },
            ],
            tooltip: {
                shared: true,
                intersect: false,
                y: {
                    formatter: (val: number, opts?: { seriesIndex?: number }) => {
                        const sIndex = opts?.seriesIndex ?? 0;
                        if (sIndex === 0) {
                            return `${Number(val).toLocaleString()} m³`;
                        } else if (sIndex === 1) {
                            return `${Number(val).toLocaleString()} m³/s`;
                        }
                        return String(val);
                    },
                },
            },
            theme: {
                mode: 'dark',
            },
        }),
        [categories, tMiningSpeed, tVolumeLeft, tSpeed],
    );

    if (isLoading) {
        return (
            <div className="d-flex justify-content-center align-items-center w-100" style={{ minHeight: 380 }}>
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">{tLoading}</span>
                </div>
            </div>
        );
    }

    if (!categories || categories.length === 0 || series.length === 0) {
        return (
            <div className="d-flex justify-content-center align-items-center text-muted text-center p-4 w-100" style={{ minHeight: 380 }}>
                {tNoData}
            </div>
        );
    }

    return (
        <Chart
            options={options}
            series={series}
            type="line"
            height={380}
            width="100%"
        />
    );
}

export default TrafficChart;
