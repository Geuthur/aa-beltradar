// React
import { Link, useLocation } from "react-router";

// Third Party
import { Nav } from "react-bootstrap"

// AA Belt Radar
import type { components } from "@/Api/OpenApi";

export type MenuLinkItem = components["schemas"]["MenuLink"];

export interface MenuCategory {
  name: string;
  link?: string;
  links?: MenuLinkItem[];
}

export interface MenuProps {
  isLoading: boolean;
  data: Array<MenuCategory | MenuLinkItem>;
  error: boolean;
}

export interface ToPath {
    toPath: (link: string) => string;
}

export const MenuItem = ({ link, toPath }: { link: MenuLinkItem } & ToPath) => {
    const path = useLocation();
    const hit = path.pathname.endsWith(link.link ?? "");
    return (
        <Nav.Item as="li">
            <Nav.Link
                as={Link}
                to={{ pathname: toPath(link.link ?? ""), search: path.search }}
                id={link.name}
                key={link.name}
                active={hit}
            >
                {link.name}
            </Nav.Link>
        </Nav.Item>
    );
};
