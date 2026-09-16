// Third Party
import type { QueryKey } from "@tanstack/react-query";

// AA Belt Radar
import type { components } from "@/Api/OpenApi";

export type MenuModalKey = keyof components["schemas"]["MenuModalSchema"];

export interface SectionHeaderProps {
    name: string;
    queryKey?: QueryKey | QueryKey[];
    modalKey?: MenuModalKey;
    buttonTitle?: string;
    buttonIcon?: string;
    validate?: (formData: Record<string, string | boolean>) => boolean;
    children?: React.ReactNode | ((props: {
        formData: Record<string, string | boolean>;
        onChange: (data: Record<string, string | boolean>) => void;
    }) => React.ReactNode);
}
