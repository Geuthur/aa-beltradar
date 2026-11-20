// Third Party
import type { QueryKey } from "@tanstack/react-query";

// AA Belt Radar
import type { SectionModalKey } from "@/Components/Modals/modalConfig";

export interface SectionHeaderProps {
    name: string;
    queryKey?: QueryKey | QueryKey[];
    modalKey?: SectionModalKey;
    buttonTitle?: string;
    buttonIcon?: React.ReactNode;
    validate?: (formData: Record<string, string | boolean>) => boolean;
    children?: React.ReactNode | ((props: {
        formData: Record<string, string | boolean>;
        onChange: (data: Record<string, string | boolean>) => void;
    }) => React.ReactNode);
}
