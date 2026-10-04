// React
import { useMemo } from 'react';

// Third Party
import type { ApexOptions } from 'apexcharts';
import Chart from 'react-apexcharts';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { ApexChartSchema } from '@/Api/schema';
import FetchingLoader from '@/Components/Loader/FetchingLoader';

export interface MiningChartProps {
    data?: ApexChartSchema | null;
    isLoading?: boolean;
}

export function MiningChart({ data, isLoading }: MiningChartProps) {
    const { t } = useTranslation();

    // Translations for tooltips and titles
    const tOreProgression = t("Ore Progression");
    const tNoData = t("No mining chart data available.");
    const tLoading = t("Loading...");

    const categories = useMemo(() => data?.categories ?? [], [data?.categories]);
    const series = useMemo(() => {
        return (data?.series ?? []).map((s) => ({
            name: s.name,
            data: s.data,
        }));
    }, [data?.series]);

    const options: ApexOptions = useMemo(
        () => ({
            chart: {
                type: 'bar',
                height: 380,
                background: 'transparent',
                foreColor: '#a1a1aa',
                toolbar: { show: false },
            },
            colors: ['#10b981'],
            grid: { borderColor: '#27272a' },
            plotOptions: {
                bar: {
                    borderRadius: 4,
                    borderRadiusApplication: 'end',
                    horizontal: true,
                    dataLabels: {
                        position: 'right',
                    },
                },
            },
            title: {
                text: tOreProgression,
            },
            dataLabels: {
                enabled: true,
                formatter: (value: number | string) => `${Number(value).toFixed(1)}%`,
            },
            xaxis: {
                categories,
                min: 0,
                max: 100,
                tickAmount: 5,
                labels: {
                    formatter: (value: string) => `${Number(value).toFixed(0)}%`,
                },
            },
            tooltip: {
                y: {
                    formatter: (value: number) => `${Number(value).toFixed(2)}%`,
                },
            },
            theme: {
                mode: 'dark',
            },
        }),
        [categories, tOreProgression],
    );

    if (isLoading) {
        return (
            <div className="br-chart-empty">
                <FetchingLoader message={tLoading} />
            </div>
        );
    }

    if (!categories || categories.length === 0 || series.length === 0) {
        return (
            <div className="br-chart-empty">
                {tNoData}
            </div>
        );
    }

    return (
        <Chart
            options={options}
            series={series}
            type="bar"
            height={380}
            width="100%"
        />
    );
}

export default MiningChart;
