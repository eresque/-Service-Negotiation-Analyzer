import React from 'react';
import classNames from 'classnames';
import './style.scss';

type BlockProps = {
    children: React.ReactNode,
    className: string,
    style?: React.CSSProperties
};

const Block = (props: BlockProps): JSX.Element => {

    const classes = classNames(
        'block ' + props.className
    );

    return(
        <div className={classes}>
            {props.children}
        </div>
    );
};

Block.defaultProps = {
    children: '',
    className: 'block',
    style: {}
};

export default Block; 