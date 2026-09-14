// Third Party
import { OverlayTrigger, Button } from "react-bootstrap";

// AA Belt Radar
import { renderTooltip } from "@/Components/Helpers/functions";

export interface ButtonProps {
	icon: string;
	onClick: () => void;
	title: string;
	color: string;
}

export function IconButton({ icon, onClick, title, color }: ButtonProps) {
	return (
        <>
            <OverlayTrigger
                trigger={["hover", "focus"]}
                overlay={renderTooltip(title)}
            >
                <Button
                    onClick={onClick}
                    title={title}
                    size="sm"
                    variant={color}
                    className="me-2">
                    <i className={icon}></i>
                </Button>
            </OverlayTrigger>
        </>
    );
}
