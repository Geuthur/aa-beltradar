// React
import type { ReactNode } from 'react';

export interface BaseSectionHeaderProps {
    name: string;
    children?: ReactNode;
}

function BaseSectionHeader({ name, children }: BaseSectionHeaderProps) {
    return (
        <section className="aa-panel br-header" aria-labelledby="session-heading">
            <h3 id="session-heading" className="aa-section-title mb-0">{name}</h3>
            {children && <div className="br-toolbar">{children}</div>}
        </section>
    );
};

export default BaseSectionHeader;
